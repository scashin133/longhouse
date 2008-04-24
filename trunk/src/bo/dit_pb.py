import generated_dit_pb

class Issue(generated_dit_pb.Issue):
    def __init__(self):
        generated_dit_pb.Issue.__init__(self)

class IssueComment_Updates(generated_dit_pb.IssueComment_Updates):
    _FIELD_ID_NAMES = {
        1: 'Summary',
        2: 'Status',
        3: 'Assign To',
        4: 'Notify Users',
        5: 'Labels'
    }

    def __init__(self):
        generated_dit_pb.IssueComment_Updates.__init__(self)

class IssueComment_Attachments(generated_dit_pb.IssueComment_Attachments):
    def __init__(self):
        generated_dit_pb.IssueComment_Attachments.__init__(self)

class IssueComment(generated_dit_pb.IssueComment):
    def __init__(self):
        generated_dit_pb.IssueComment.__init__(self)

class UserIssueStars(generated_dit_pb.UserIssueStars):
    def __init__(self):
        generated_dit_pb.UserIssueStars.__init__(self)

class IssueUserStars(generated_dit_pb.IssueUserStars):
    def __init__(self):
        generated_dit_pb.IssueUserStars.__init__(self)

class IssueAttachmentContent(generated_dit_pb.IssueAttachmentContent):
    def __init__(self):
        generated_dit_pb.IssueAttachmentContent.__init__(self)

class ProjectIssueConfig_Well_known_statuses(generated_dit_pb.ProjectIssueConfig_Well_known_statuses):
    def __init__(self):
        generated_dit_pb.ProjectIssueConfig_Well_known_statuses.__init__(self)

class ProjectIssueConfig_Well_known_labels(generated_dit_pb.ProjectIssueConfig_Well_known_labels):
    def __init__(self):
        generated_dit_pb.ProjectIssueConfig_Well_known_labels.__init__(self)

class ProjectIssueConfig_Well_known_prompts(generated_dit_pb.ProjectIssueConfig_Well_known_prompts):
    def __init__(self):
        generated_dit_pb.ProjectIssueConfig_Well_known_prompts.__init__(self)

class ProjectIssueConfig_Canned_queries(generated_dit_pb.ProjectIssueConfig_Canned_queries):
    def __init__(self):
        self.search_engine_query = ""
        generated_dit_pb.ProjectIssueConfig_Canned_queries.__init__(self)
        
    def set_search_engine_query(self, se_query):
        self.search_engine_query = se_query

    def get_search_engine_query(self):
        return self.search_engine_query


class ProjectIssueConfig(generated_dit_pb.ProjectIssueConfig):
    def __init__(self):
        generated_dit_pb.ProjectIssueConfig.__init__(self)
    
    def get_developer_prompts(self):
        print 'getting developer prompts'
        developer_prompts = []
        for wkp in self.well_known_prompts_:
            if wkp.prompt_name().startswith('Developer'):
                developer_prompts.append(wkp)
        return developer_prompts
    
    def get_user_prompts(self):
        user_prompts = []
        for wkp in self.well_known_prompts_:
            if wkp.prompt_name().startswith('User'):
                user_prompts.append(wkp)
        return user_prompts

