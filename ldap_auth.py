import ldap

LDAP_SERVER = "1270.0.0.1"
LDAP_PORT = 389

def authenticate(username, password):
  if not username:
    print "Username is empty"
    return None
  if not password:
    print "Password is empty"
    return None
  try:
    ld = ldap.open(LDAP_SERVER, port=LDAP_PORT)
    ld.simple_bind_s(username, password)
    print "[Username: ", username, "] sucessfully authenticated to server."
    return ld
  except ldap.INVALID_CREDENTIALS, error_message:
    print "[Username: ", username, "] INVALID_CREDENTIALS: %s " % error_message
    return None
  except Exception, error_message:
    print "[Username: ", username, "] EXCEPTION: %s " % error_message
  return None

def hasMembershipWithSession(username, session, membership):
  try:
    if not session:
      return False
    session.set_option(ldap.OPT_REFERRALS, 0)
    result = session.search_s('DC=site4, DC=cdc, DC=com', ldap.SCOPE_SUBTREE, 'CN=' + username, ['memberOf'])
    return membership in str(result)
  except Exception:
    return False
  
def hasMembership(username, password, membership):
  session = authenticate(username, password)
  return hasMembershipWithSession(username, session, membership)

def unauthenticate(session):
    session.unbind_s()
    return True