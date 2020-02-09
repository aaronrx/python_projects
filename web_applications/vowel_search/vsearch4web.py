#!/usr/bin/env python3
from flask import Flask, render_template, request, session, copy_current_request_context
from vsearch import search4letters
from DBcm import UseDatabase, ConnectionError, CredentialsError, SQLError
from checker import check_logged_in
from time import sleep
from threading import Thread

__author__ = 'Aaron Rioflorido'

__version__ = (
    'Added threading and copy_current_request_context, 8/12/2019'
    'Added various exception handling codes, 7/12/2019'
    'Added login feature using session, 28/10/2019',
    'vsearch webapp 1.0, 27/10/2019'
)

app = Flask(__name__)

# Webapp's secret key (which enables the use of sessions)
app.secret_key = 'YouWillNeverGuess'

# Flask's built-in dictionary configuration
app.config['dbconfig'] = {'host': '127.0.0.1',
                          'user': 'vsearch',
                          'password': 'vsearchpasswd',
                          'database': 'vsearchlogDB'}


@app.route('/search4', methods=['POST'])
def do_search() -> 'html':
    """Returns search results"""
    # This function is decorated in a way that the /search4 URL only supports the POST method
    # (meaning GET requests are no longer supported)

    @copy_current_request_context
    def log_request(req: 'flask_request', res: str) -> None:
        """Log details of the web request and the results."""
        # This function is decorated with flask's copy_current_request_context which makes the request and results
        # variables available even after the do_search() has completed its processing

        # Artificial delay to simulate DB connection delay
        sleep(2)

        try:
            with UseDatabase(app.config['dbconfig']) as cursor:
                # insert statement (with data placeholders)
                _SQL_INSERT = """insert into log
                                (phrase, letters, ip, browser_string, results)
                                values (%s, %s, %s, %s, %s)
                                """

                # data to be logged to the database
                insert_values = (req.form['phrase'], req.form['letters'],
                                 req.remote_addr, req.user_agent.browser,
                                 res)

                cursor.execute(_SQL_INSERT, insert_values)

        except ConnectionError as err:
            print('Is your database switched on? Error: ', str(err))
        except CredentialsError as err:
            print('Database User-id/Password issues. Error: ', str(err))
        except SQLError as err:
            print('Is your query correct? Error:', str(err))
        except Exception as err:
            print('Something went wrong: ', str(err))
        return 'Error'

    phrase = request.form['phrase']
    letters = request.form['letters']
    title = 'Here are your results:'
    results = str(search4letters(phrase, letters))

    try:
        t = Thread(target=log_request, args=(request, results))
        t.start()
    except Exception as err:
        print('***** Logging failed with this error:', str(err))

    return render_template('results.html',
                           the_title=title, the_results=results,
                           the_phrase=phrase, the_letters=letters,)


@app.route('/')
@app.route('/entry')
def entry_page() -> 'html':
    """This function is the home page and associated with it are '/' and '/entry' pages"""
    return render_template('entry.html',
                           the_title='Welcome to search4letters on the web!')


@app.route('/viewlog')
@check_logged_in
def view_the_log() -> 'html':
    """Access the database to fetch the logged data"""

    try:
        with UseDatabase(app.config['dbconfig']) as cursor:
            _SQL_SELECT = """select ts, phrase, letters, ip, browser_string, results
                             from log"""

            cursor.execute(_SQL_SELECT)
            contents = cursor.fetchall()

        titles = ('Time Stamp', 'Phrase', 'Letters', 'Remote_addr', 'User_agent', 'Results')

        return render_template('viewlog.html',
                               the_title='View Log',
                               the_row_titles=titles,
                               the_data=contents)

    except ConnectionError as err:
        print('Is your database switched on? Error: ', str(err))
    except CredentialsError as err:
        print('Database User-id/Password issues. Error: ', str(err))
    except SQLError as err:
        print('Is your query correct? Error:', str(err))
    except Exception as err:
        print('Something went wrong: ', str(err))
    return 'Error'


# Route for handling the login page logic
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != 'admin' or request.form['password'] != 'admin':
            error = 'Invalid Credentials. Please try again.'
        else:
            # return redirect(url_for('home'))
            session['logged_in'] = True
            return 'Welcome admin!'
    return render_template('login.html', error=error)


@app.route('/logout')
@check_logged_in
def do_logout() -> str:
    # Remove logged_in key from session
    session.pop('logged_in')
    return 'You are now logged out.'


# This ensures that the "app.run()" only runs when executed directly by Python
if __name__ == '__main__':
    # Switches on debugging mode ; Automatically restarts your webapp every time Flask notices your code changed
    app.run(debug=True)
