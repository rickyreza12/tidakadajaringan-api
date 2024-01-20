from flask import Flask, request, jsonify
from selenium import webdriver
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile
from selenium.common.exceptions import NoSuchElementException
import os

app = Flask(__name__)

platform = "windows" if os.name == "nt" else "linux"

# Set the path to the locally uploaded geckodriver
geckodriver_path = os.path.join(os.getcwd(), "bin\\", platform + "\\geckodriver")

if platform == "windows":
    service = Service(executable_path=geckodriver_path + ".exe")
else:
    service = Service(executable_path=geckodriver_path)

firefox_options = FirefoxOptions()
firefox_options.headless = True

# firefox_binary_path = 'C:\\Program Files\\Mozilla Firefox\\firefox.exe'
# firefox_options.binary_location = firefox_binary_path

firefox_profile = FirefoxProfile()
firefox_profile.add_argument("-profile")
firefox_profile.add_argument("{firefox_profile_path}")

capabilities = {
    "browserName": "firefox",
    "moz:firefoxOptions": {
        "args": ["-headless"],
    },
}

driver = webdriver.Firefox(options=firefox_options, service=service, capabilities=capabilities)


@app.route('/')
def hello():
    return jsonify({"msg":"test done"})

@app.route('/execute_selenium', methods=['POST'])
def execute_selenium():
    data = request.get_json()

    # Your Selenium
    url = data.get("url")
    username = data.get("user")
    password = data.get("password")
    driver.get(url)

    try:
        user_name_input = driver.find_element("id", "user_name")
        user_name_input.send_keys(username)

        password_input = driver.find_element("id", "loginpp")
        password_input.send_keys(password)

        login_button = driver.find_element("id", "login_btn")
        login_button.click()

        try:
            login_error_hint = driver.find_element("id", "login_error_hint")
            error_message = login_error_hint.text

            if error_message.strip() != "":
                result = {'status': 'error', 'message': error_message}
                return jsonify(result)
        except NoSuchElementException:
            pass

        result = {'status': 'success', 'message': 'Login successful'}
        return jsonify(result)
    except Exception as e:
        result = {'status': 'error', 'message': str(e)}
        return jsonify(result)

@app.route('/change_password', methods=['POST'])
def change_password():
    data = request.get_json()

    modify_url = data.get("url")
    password = data.get("password")
    new_password = data.get("new_password")
    driver.get(modify_url)

    try:
        result_from_go_to_network = go_to_network(driver, password, new_password)

        if result_from_go_to_network['status'] == 'error':
            return jsonify(result_from_go_to_network)

        result = {'status': 'success', 'message': 'Modification successful', 'go_to_network_result': result_from_go_to_network}
        return jsonify(result)
    except Exception as e:
        result = {'status': 'error', 'message': str(e)}
        return jsonify(result)

def go_to_network(driver, password, new_password):
    try:
        # Retrieve data from password input field 
        password_input = driver.find_element("id", "PreSharedKey")
        password_data_before = password_input.get_attribute("value")
        
        if password != password_data_before:
             result = {'status': 'success', 'message': 'the current password is wrong'}
             return result
        
        password_input.send_keys(new_password)
        password_data_after = password_input.get_attribute("value")

        result = {'status': 'success', 'message': 'Modification successful', 'password_before': password_data_before, 'password_after': password_data_after}
        return result
    except NoSuchElementException as e:
        traceback_str = traceback.format_exc()
        result = {'status': 'error', 'message': 'Apply button not found or password input not found', 'traceback': traceback_str}
        return result
    except Exception as e:
        traceback_str = traceback.format_exc()
        result = {'status': 'error', 'message': str(e), 'traceback': traceback_str}
        return result

if __name__ == '__main__':
    app.run(debug=True)
