# Extending Longhouse #

## Adding a new page ##

You might want to add a new page to Longhouse if you have an idea for a feature that currently isn't implemented in Longhouse. Luckily, adding a new page to Longhouse is easy.

Pages have two components: the template used to describe what appears on it, and the Python file that defines how to get the information from Longhouse data to show on the page, and how to act if the page has a form.

Let's start with the Python file about the page.

Create a new Python file. Where this is placed depends on what the page is. For most system pages, you want to place this Python file in the `/demetrius` directory. This is where the general pages go, such as the home page, log in, creating a project and showing project information.

Let's say that I want to make a page called `SilverBullet`. This page will be a simple "Hello World"-type page that displays the user's username, greets the user, and shows how many projects the user is a member of if the user is logged in, and otherwise warns the user that the user is not logged in.

In `/demetrius`, I create `silverbullet.py`. The first part of `silverbullet.py` will be the following:

```
import sys

from common import post
from common import http
from common import ezt_google

import framework.helpers

from demetrius import constants
from demetrius import pageclasses
from demetrius import helpers
from demetrius import permissions

class SilverBulletPage(pageclasses.DemetriusPage):
```

Next, we need to specify where the template to associate with this page is. We'll add it later, but let's assume it's going to be at `/demetrius/silverbullet.ezt'` inside `/templates`. We add, as the first line of the class:

`_PAGE_TEMPLATE = '/demetrius/silverbullet.ezt'`

Next, we need to make a method called `GatherPageData`. This is the method in which you would call the persistence methods of Longhouse in order to get data to render on the page. This method needs to return a dictionary, with the keys of the dictionary being the names you will refer to on the EZT template, and the values being the objects you want to pass to the EZT template in order to fill in information.

Let's get the number of projects that the user is a member of. Our `GatherPageData` method will look like this:

```
	def GatherPageData(self, request, req_info):
		if req_info.logged_in_user_id is not None:
			number_of_projects = req_info.logged_in_user.member_of_projects_size()
			page_data = {
				'number_of_projects': number_of_projects
			}
        else:
			page_data = {}
        return page_data
```

That's it for the page logic itself. Now we need to register the page to a desired URL. In `/demetrius/constants.py` let's add the following:

`SILVER_BULLET_PAGE_URL = '/silverbullet'`

Make sure the URL you choose isn't taken by another page already in the `constants.py` file.

Now, go to `/demetrius/page_setup.py`. This is where we add the Handler for the page you created. (Don't worry, you don't have to write the Handler object yourself.)

In the import section, add the line:

`from demetrius import silverbullet`

Now, let's register the page. Since it isn't a page that is different for each project, we should just add it as a cross-site page. In `RegisterSiteHandlers()`, let's add these lines:

```
    silver_bullet_page = silverbullet.SilverBulletPage(
      self.conn_pool, self.demetrius_persist, self.universal_ezt_data)
    self._SetupUserPage(silver_bullet_page.Handler,
                           constants.SILVER_BULLET_PAGE_URL)
```

Now that that's done, we only need to create the template. Let's create a new text document at `/templates/demetrius/silverbullet.ezt`, since that's the URL we specified in the `SilverBulletPage` class.

Here's what we'd write for the template:

```
[define title]Silver Bullet Page[end]

[define breadcrumbs]
<span class="item">Magic Silver Bullet Page</span>
[end]

[include "master-header.ezt" "notabs"]

[if-any number_of_projects]
	Hello, [logged_in_user.display_name]! You're a member of [number_of_projects].
[else]
	Hello, un-logged-in user! The only silver bullet is to register an account and log in.
[end]

[include "master-footer.ezt"]

```