package server

import (
	"app/internal/api_errors"
	"app/internal/db"
	"bytes"
	"context"
	"encoding/base64"
	"encoding/json"
	"errors"
	"fmt"
	"io"
	"log"
	"net/http"
	"strings"
	"time"
)

type TokenResponse struct {
	AccessToken  string          `json:"access_token"`
	RefreshToken string          `json:"refresh_token"`
	ExpiresIn    int             `json:"expires_in"`
	User         json.RawMessage `json:"user"`
}

type GoogleTokenRequest struct {
	Credential string `json:"credential"`
}

type User struct {
	ID string `json:"id"`
}

func (s *Server) HandleGoogleAuth(w http.ResponseWriter, r *http.Request) error {
	var req GoogleTokenRequest
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		return &api_errors.ClientErr{
			HttpCode: http.StatusBadRequest,
			Message:  "Invalid request",
		}
	}

	tokenResp, err := s.exchangeGoogleToken(req.Credential)
	if err != nil {
		return &api_errors.ClientErr{
			HttpCode: http.StatusUnauthorized,
			Message:  "Authentication failed",
		}
	}

	session, _ := s.store.Get(r, "auth-session")
	session.Values["access_token"] = tokenResp.AccessToken
	session.Values["refresh_token"] = tokenResp.RefreshToken
	session.Values["expires_at"] = time.Now().Add(time.Duration(tokenResp.ExpiresIn) * time.Second)

	if err := session.Save(r, w); err != nil {
		return errors.New(err.Error())
	}

	w.WriteHeader(http.StatusOK)
	return nil
}

func (s *Server) HandleLogout(w http.ResponseWriter, r *http.Request) error {
	session, _ := s.store.Get(r, "auth-session")
	session.Options.MaxAge = -1
	session.Save(r, w)
	http.Redirect(w, r, "/login", http.StatusSeeOther)
	return nil
}

// AuthPageMiddleware handles authentication for page requests
// Returns redirects for unauthenticated users
func (s *Server) AuthPageMiddleware(next http.Handler) http.Handler {
	return NewHandler(func(w http.ResponseWriter, r *http.Request) error {
		session, _ := s.store.Get(r, "auth-session")
		accessToken, ok := session.Values["access_token"].(string)
		if !ok {
			http.Redirect(w, r, "/login", http.StatusSeeOther)
			return nil
		}

		expiresAt, ok := session.Values["expires_at"].(time.Time)
		if !ok || time.Until(expiresAt) < 5*time.Minute {
			refreshToken, ok := session.Values["refresh_token"].(string)
			if !ok {
				http.Redirect(w, r, "/login", http.StatusSeeOther)
				return nil
			}

			tokenResp, err := s.refreshToken(refreshToken)
			if err != nil {
				http.Redirect(w, r, "/login", http.StatusSeeOther)
				return nil
			}

			session.Values["access_token"] = tokenResp.AccessToken
			session.Values["refresh_token"] = tokenResp.RefreshToken
			session.Values["expires_at"] = time.Now().Add(time.Duration(tokenResp.ExpiresIn) * time.Second)
			session.Save(r, w)

			accessToken = tokenResp.AccessToken
		}

		userID, err := parseUserIDFromToken(accessToken)
		if err != nil {
			return err
		}

		isAuth, err := db.IsAuthUser(userID)
		if err != nil {
			return err
		}
		if !isAuth {
			log.Print("User not authorized for private beta")
			http.Redirect(w, r, "/login", http.StatusSeeOther)
			return nil
		}

		ctx := context.WithValue(r.Context(), "token", accessToken)
		next.ServeHTTP(w, r.WithContext(ctx))
		return nil
	})
}

// AuthAPIMiddleware handles authentication for API requests
// Returns JSON errors for unauthenticated users
func (s *Server) AuthAPIMiddleware(next http.Handler) http.Handler {
	return NewHandler(func(w http.ResponseWriter, r *http.Request) error {
		session, _ := s.store.Get(r, "auth-session")
		accessToken, ok := session.Values["access_token"].(string)
		if !ok {
			return &api_errors.ClientErr{
				HttpCode: http.StatusUnauthorized,
				Message:  "Authentication required",
			}
		}

		expiresAt, ok := session.Values["expires_at"].(time.Time)
		if !ok || time.Until(expiresAt) < 5*time.Minute {
			refreshToken, ok := session.Values["refresh_token"].(string)
			if !ok {
				return &api_errors.ClientErr{
					HttpCode: http.StatusUnauthorized,
					Message:  "Invalid session",
				}
			}

			tokenResp, err := s.refreshToken(refreshToken)
			if err != nil {
				return &api_errors.ClientErr{
					HttpCode: http.StatusUnauthorized,
					Message:  "Session refresh failed",
				}
			}

			session.Values["access_token"] = tokenResp.AccessToken
			session.Values["refresh_token"] = tokenResp.RefreshToken
			session.Values["expires_at"] = time.Now().Add(time.Duration(tokenResp.ExpiresIn) * time.Second)
			session.Save(r, w)

			accessToken = tokenResp.AccessToken
		}

		userID, err := parseUserIDFromToken(accessToken)
		if err != nil {
			return err
		}

		isAuth, err := db.IsAuthUser(userID)
		if err != nil {
			return err
		}
		if !isAuth {
			return &api_errors.ClientErr{
				HttpCode: http.StatusUnauthorized,
				Message:  "User not authorized for private beta",
			}
		}

		ctx := context.WithValue(r.Context(), "token", accessToken)
		ctx = context.WithValue(ctx, "userId", userID)

		next.ServeHTTP(w, r.WithContext(ctx))
		return nil
	})
}

type JWTClaims struct {
	Sub string `json:"sub"`
}

func parseUserIDFromToken(tokenString string) (string, error) {
	parts := strings.Split(tokenString, ".")
	if len(parts) != 3 {
		return "", fmt.Errorf("invalid token format")
	}

	payload, err := base64.RawURLEncoding.DecodeString(parts[1])
	if err != nil {
		return "", err
	}

	var claims JWTClaims
	if err := json.Unmarshal(payload, &claims); err != nil {
		return "", err
	}

	return claims.Sub, nil
}

func (s *Server) exchangeGoogleToken(idToken string) (*TokenResponse, error) {
	body := map[string]interface{}{
		"id_token": idToken,
		"provider": "google",
	}
	return s.supabaseAuthRequest("/auth/v1/token?grant_type=id_token", body)
}

func (s *Server) supabaseAuthRequest(path string, body interface{}) (*TokenResponse, error) {
	jsonBody, _ := json.Marshal(body)

	req, err := http.NewRequest("POST", s.projectURL+path, bytes.NewBuffer(jsonBody))
	if err != nil {
		return nil, err
	}

	req.Header.Set("apikey", s.anonKey)
	req.Header.Set("Content-Type", "application/json")

	resp, err := http.DefaultClient.Do(req)
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()

	respBody, _ := io.ReadAll(resp.Body)

	if resp.StatusCode != http.StatusOK {
		return nil, fmt.Errorf("auth failed: status=%d body=%s", resp.StatusCode, respBody)
	}

	var tokenResp TokenResponse
	if err := json.NewDecoder(bytes.NewReader(respBody)).Decode(&tokenResp); err != nil {
		return nil, fmt.Errorf("decoding response: %w", err)
	}

	return &tokenResp, nil
}

func (s *Server) refreshToken(refreshToken string) (*TokenResponse, error) {
	body := map[string]interface{}{
		"refresh_token": refreshToken,
	}
	return s.supabaseAuthRequest("/auth/v1/token?grant_type=refresh_token", body)
}
