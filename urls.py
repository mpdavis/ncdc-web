import views


def add_urls(app):
    app.add_url_rule('/', view_func=views.Home.as_view('home'))
    app.add_url_rule('/about/', view_func=views.About.as_view('about'))
    app.add_url_rule('/login/', view_func=views.Login.as_view('login'))
    app.add_url_rule('/payroll/', view_func=views.Payroll.as_view('payroll'))
    app.add_url_rule('/approve/', view_func=views.Approve.as_view('approve'))