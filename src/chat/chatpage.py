import sys

from common import post
from common import http
from common import ezt_google

import framework.helpers

from demetrius import constants
from demetrius import pageclasses
from demetrius import helpers
from demetrius import permissions

import chat.constants

class ChatPage(pageclasses.DemetriusPage):

    _PAGE_TEMPLATE = '/chat/chatpage.ezt'
    _MAIN_TAB_MODE = constants.MAIN_TAB_CHAT
    
    def GatherPageData(self, request, req_info):
        if req_info.logged_in_user_id is not None:
        
            #number_of_projects = req_info.logged_in_user.member_of_projects_size()
        
            page_data = {
                # chat username for "user1@gmail.com" is "user1"
                'chat_username': req_info.logged_in_user.display_name.split('@')[0]
            }
        
        else:
            page_data = {}
        
        return page_data    
    
    
    
    
    