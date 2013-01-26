import views


def add_urls(app):
    app.add_url_rule('/', view_func=views.Home.as_view('home'))
    app.add_url_rule('/about/', view_func=views.About.as_view('about'))
    app.add_url_rule('/login/', view_func=views.Login.as_view('login'))
    app.add_url_rule('/logout/', view_func=views.Login.as_view('logout'))
    app.add_url_rule('/payroll/<payroll_user>/<week>/', view_func=views.Payroll.as_view('payroll'))
    app.add_url_rule('/payroll/<payroll_user>/', view_func=views.Payroll.as_view('payroll'))
    app.add_url_rule('/payroll/', view_func=views.Payroll.as_view('payroll'))
    app.add_url_rule('/approve/', view_func=views.Approve.as_view('approve'))
    app.add_url_rule('/admin/', view_func=views.Admin.as_view('admin'))
    app.add_url_rule('/add_user/', view_func=views.AddUser.as_view('add_user'))
    app.add_url_rule('/delete_user/', view_func=views.DeleteUser.as_view('delete_user'))