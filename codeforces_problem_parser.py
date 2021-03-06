import sublime
import sublime_plugin
import urllib.request
import os
import re

# Keep track of the last opened program
last_url = ''

# Load the settings file, ideally this should be called once and only once


def load_settings():
    settings = sublime.load_settings('CodeforcesUtil.sublime-settings')
    return settings


# The main folder where the folder of the current program should be created
def get_parent_dir(settings, title):
    parent_dir = settings.get('parent_dir', '.')
    return os.path.join(parent_dir, title)


# Get the extensions of the file
def get_extension(settings):
    return settings.get('extension', '')


# Create the program file
# TODO: make this method not dependent on any programming language
def createFile(dir_path, title, extension):
    if not os.path.exists(dir_path):
        os.makedirs(dir_path, mode=0o777)
        os.chmod(dir_path, 0o777)
    filename = os.path.join(dir_path, title + '.' + extension)
    try:
        open(filename, "a").close()
        return filename
    except Exception as e:
        print ("Exception: ", e)
        sublime.error_message(
            "Unable to create file: 'Permission denied'," +
            " please specify another folder in Codeforces.sublime-settings" +
            " or change the permissions of the folder")
        return None


# Extract the title of the program
def get_title(url):
    from bs4 import BeautifulSoup
    global last_url
    last_url = url
    try:
        reponse = urllib.request.urlopen(url)
    except Exception as e:
        print (e)
        sublime.error_message("Wrong url: " + url)
        return
    page = reponse.read()
    soup = BeautifulSoup(page, 'html.parser')
    title = soup.find('div', attrs={'class': 'problem-statement'}
                      ).find('div', attrs={'class': 'title'}).text[2:].strip()
    title = re.sub(r'[^\w]+', '_', title)
    return title


# Fetch the program using bs
def fetch(self, url):
    if url is None or url.strip() == '':
        return
    title = get_title(url)
    settings = load_settings()
    dir_path = get_parent_dir(settings, title)
    extension = get_extension(settings)
    file = createFile(dir_path, title, extension)
    if file is None:
        return

    snippets_file_name = settings.get('snippets', None)
    snippets_content = ''
    if snippets_file_name is not None:
        snippets_file = open(snippets_file_name)
        try:
            snippets_content = snippets_file.readlines()
            snippets_file.close()
        except Exception as e:
            sublime.error_message("File not found " + snippets_file)
            print (e)
            snippets_file.close()
            return

    open(file, 'w').writelines(snippets_content)
    sublime.active_window().open_file(file)


class CodeforcesProblemCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        def on_done(url):
            fetch(self, url)

        sublime.active_window().show_input_panel(
            "Enter program url",
            last_url,
            on_done,
            None,
            None)
