import pickle , os
from classes import Que
just_started = True
contact_bus = Que()
intermediate_bus = Que()
intermediate_contact_ids = []
if os.path.exists('contact_ids.pickle'):
    with open('contact_ids.pickle','rb') as fp:
        contact_ids = pickle.load(fp)
else:
    contact_ids = []


page = 0