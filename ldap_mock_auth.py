def authenticate(username, password):
  if username == "bob" and password == "bob":
      return True
  elif username == "jim" and password == "jim":
      return True
  elif username == "ben" and password == "ben":
      return True
  else:
      return False

def hasMembershipWithSession(username, session, membership):
  if username == "bob" and membership == "TimesheetApprover":
      return True
  elif username == "jim" and membership == "TimesheetAdmin":
      return True
  else:
      return False
  
def hasMembership(username, password, membership):
  if username == "bob" and membership == "TimesheetApprover":
      return True
  elif username == "jim" and membership == "TimesheetAdmin":
      return True
  else:
      return False

def unauthenticate(session):
  return True