from playwright.sync_api import sync_playwright
import json


def capture_auth_data(email, password):
    auth_data = {}

    def handle_request(request):
        if "userLogin" in request.url:
            auth_data['login_payload'] = request.post_data

    def handle_response(response):
        if "userLogin" in response.url:
            auth_data['login_response'] = response.json()

        # Capture cookies after successful login
        if response.status == 200 and "userLogin" in response.url:
            auth_data['cookies'] = context.cookies()

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()

        # Set up request/response interception
        context.on("request", handle_request)
        context.on("response", handle_response)

        page = context.new_page()

        try:
            page.goto("https://web.tulotero.es/")
            page.wait_for_selector('form input[name="username"]', timeout=10000)
            page.fill('form input[name="username"]', email)
            page.fill('tl-input-password input[type="password"]', password)
            page.click('button.btn-login')
            page.wait_for_load_state('networkidle')

            # Capture local storage and session storage
            auth_data['local_storage'] = page.evaluate("() => JSON.stringify(Object.entries(localStorage))")
            auth_data['session_storage'] = page.evaluate("() => JSON.stringify(Object.entries(sessionStorage))")

            # Capture headers of a subsequent request (adjust the URL as needed)
            subsequent_request = page.request.get("https://web.tulotero.es/api/some-endpoint")
            auth_data['request_headers'] = subsequent_request.headers
        except Exception as e:
            print(f"An error occurred: {e}")
        finally:
            browser.close()

    return auth_data


email = "a.jaenrev@gmail.com"
password = "ig*Br$qTS!0"
auth_data = capture_auth_data(email, password)

print("Captured Authentication Data:")
print(json.dumps(auth_data, indent=2))

# Save to a file (be cautious with this sensitive data)
with open("tulotero_auth_data.json", "w") as f:
    json.dump(auth_data, f, indent=2)

print("Auth data saved to tulotero_auth_data.json")
