import views


def add_urls(app):
    """
    Helper function for adding url rules to the application.  Any url answered by the application
    has to be mapped to a view function here.

    :param app: The Flask app running the application.
    """
    app.add_url_rule('/', view_func=views.Home.as_view('home'))
    app.add_url_rule('/about/', view_func=views.About.as_view('about'))
    app.add_url_rule('/login/', view_func=views.Login.as_view('login'))
    app.add_url_rule('/logout/', view_func=views.Logout.as_view('logout'))
    app.add_url_rule('/payroll/<payroll_user>/<week>/', view_func=views.Payroll.as_view('payroll'))
    app.add_url_rule('/payroll/<payroll_user>/', view_func=views.Payroll.as_view('payroll'))
    app.add_url_rule('/payroll/', view_func=views.Payroll.as_view('payroll'))
    app.add_url_rule('/approve/', view_func=views.Approve.as_view('approve'))
    app.add_url_rule('/admin/', view_func=views.Admin.as_view('admin'))
    app.add_url_rule('/add_user/', view_func=views.AddUser.as_view('add_user'))
    app.add_url_rule('/delete_user/', view_func=views.DeleteUser.as_view('delete_user'))
    app.add_url_rule('/get_info/<username>/', view_func=views.GetInfo.as_view('get_info'))
    app.add_url_rule('/get_users/', view_func=views.GetUsers.as_view('get_users'))