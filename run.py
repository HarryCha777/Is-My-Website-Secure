from flask import Flask, render_template, url_for, request
import subprocess, smtplib, json

app = Flask(__name__)

@app.route("/")
@app.route("/home")
def home():
    return render_template('home.html')

@app.route("/input-error")
def inputError():
    return render_template('input-error.html')

@app.route("/results", methods = ['POST'])
def results():
    websiteURL = request.form['website']

    # make sure the input is only one word
    if len(websiteURL) == 0:
        message = "The URL is not provided. Please provide an input."
        return render_template('home.html', message=message)
    elif len(websiteURL.split()) > 1:
        message = "More than one input is provided: \"" + websiteURL + "\". Please provide only one URL input."
        return render_template('home.html', message=message)

    originalWebsiteURL = websiteURL
    if websiteURL.startswith("http://"):
        websiteURL = websiteURL[7:]
    if websiteURL.startswith("https://"):
        websiteURL = websiteURL[8:]
    output = subprocess.check_output(["nmap", websiteURL, "-F", "-T5"])
    outputList = output.decode("utf-8").split("\n")

    # make sure the website with the provided URL exists
    if outputList[len(outputList)-2].startswith('Nmap done: 0'):
        message = "The website with the provided URL \"" + websiteURL + "\"  does not exist. Please make sure that there is no typo and provide a valid URL."
        return render_template('home.html', message=message)

    for i in range(len(outputList)):
        if len(outputList[i]) > 0 and outputList[i][0].isdigit():
            startIndex = i
            break
    outputList = outputList[startIndex:len(outputList)-3]
    for i in range(len(outputList)):
        wordList = outputList[i].split()
        if wordList[0].find('tcp') != -1:
            resultOutput = "TCP port "
        else:
            resultOutput = "UDP port "
        resultOutput += wordList[0][:wordList[0].find("/")] + " is "
        if wordList[2] == "unknown":
            resultOutput += wordList[1] + " and is running an unknown service."
        else:
            resultOutput += wordList[1] + " and is running service \"" + wordList[2] + "\"."
        outputList[i] = resultOutput
    header = "Port Scan Result of Website \"" + originalWebsiteURL + "\":"
    outputList.append("\n")
    outputList.append("After viewing the report, please be sure to keep open only the ports your website requires.")
    outputList.append("Immediately close the ports running services you do not need or recognize, which are potential vulnerabilities.")

    return render_template('results.html', outputList=outputList, header=header)

@app.route("/contact")
def contact():
    return render_template('contact.html')

@app.route("/contacting", methods = ['POST'])
def contacting():
    name = request.form['name']
    email = request.form['email']
    subject = request.form['subject']
    message = request.form['message']
    fullMessage = "\r\nName: " + name + "\r\nEmail: " + email + "\r\nSubject: " + subject + "\r\nMessage:\r\n" + message    

    with open('/etc/config.json') as config_file:
        config = json.load(config_file)
    s = smtplib.SMTP('smtp.gmail.com', 587)
    s.starttls()
    s.login(config['EMAIL_USER'], config['EMAIL_PASS'])
    s.sendmail(config['EMAIL_USER'], config['EMAIL_USER'], fullMessage)	
    s.quit()
    #config.close()

    return render_template('contact.html', success=True)

@app.route("/privacy")
@app.route("/privacy-policy")
def privacyPolicy():
    return render_template('privacy-policy.html')

@app.errorhandler(404)
def error404(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(403)
def error403(error):
    return render_template('errors/403.html'), 403

@app.errorhandler(500)
@app.errorhandler(Exception)
def error500(error):
    return render_template('errors/500.html'), 500

if __name__ == '__main__':
    app.run(debug=True)
