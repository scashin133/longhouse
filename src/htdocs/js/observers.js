document.observe("dom:loaded", function(){
	
	function acofMemberHandler(e){
        memberJSON = arguments[1];

        eventElement = Event.element(e);

        aclist = $('ac-list');
        aclist.innerHTML = "";
        aclist.insert(new Element("table").insert(tbody = new Element("tbody")));
        
        if(eventElement.readAttribute("name") == "cc"){
            ccValues = eventElement.readAttribute("value");
            
            newMembersJSON = [];
            
            memberJSON.each(function(item){
               name = item.name;
               if(!ccValues.include(name)){
                   newMembersJSON.push(item);
               } 
            });
            
            if(!ccValues.blank()){memberJSON = newMembersJSON;}
            
        }
        
        counter = 0
        if(memberJSON.size() > 0){
            memberJSON.each(function(j){
              if(counter == 0){
                tbody.insert(new Element("tr", {"class" : "acse acmo selected"}).insert(new Element("td").insert(j.name)));
              } else {
                tbody.insert(new Element("tr", {"class" : "acse acmo"}).insert(new Element("td").insert(j.name)));
              }
              counter++;
            });
    
            cOffset = Element.cumulativeOffset(eventElement);

            aclist.setStyle({
              top: (cOffset[1] + eventElement.getHeight()).toPaddedString(0) + "px",
              left: cOffset[0].toPaddedString(0) + "px",
              position: "absolute"
            });
    
            aclist.show();

            $$('tr.acmo').each(function(element){
              Event.observe(element, 'mouseover', function(e){
                $$('tr.selected').each(function(element){
                  element.removeClassName('selected');
                });
                element.addClassName('selected');
              });      
            });
    
            $$('tr.acse').each(function(element){
              Event.observe(element, 'click', function(e){        
                oldValue = eventElement.readAttribute("value");
        
                // Check to see if it is a cc list cause then need to comma seperate the list
                if(eventElement.readAttribute("name") == "cc"){
                    // add a comma and a space to the end if there is none
                    if(!oldValue.empty() && !oldValue.endsWith(", ")){
                        oldValue = oldValue + ", ";
                    }
                    eventElement.writeAttribute({value : oldValue + Event.element(e).innerHTML + ", "});
                } else {
                    eventElement.writeAttribute({value : Event.element(e).innerHTML});
                }
                aclist = $('ac-list');
                aclist.innerHTML = "";
                aclist.hide();
              });
        });
    } else {
        cOffset = Element.cumulativeOffset(eventElement);
        
        tbody.insert(new Element("tr").insert(new Element("td").insert("You have selected all project members.")));
        
        aclist.setStyle({
          top: (cOffset[1] + eventElement.getHeight()).toPaddedString(0) + "px",
          left: cOffset[0].toPaddedString(0) + "px",
          position: "absolute"
        });

        aclist.show();
    }
    

    
	}
	
	function acmoHandler(e){
	  hoveredElement = Event.element(e);
	  hoveredElement.addClassName("selected");	  
	}
	
	function acofOptionsHandler(e){
	    optionsArray = arguments[1];

        eventElement = Event.element(e);

        aclist = $('ac-list');
        aclist.innerHTML = "";
        aclist.insert(new Element("table").insert(tbody = new Element("tbody")));
        
        counter = 0
        
        optionsArray.each(function(optionArrayItem){
            if(optionsArray.size() > 1){
                tbody.insert(new Element("th").insert(optionArrayItem.name));
            }
            
            optionArrayItem.values.each(function(valueItem){
                if(counter == 0){
                  tbody.insert(new Element("tr", {"class" : "acse acmo selected"}).insert(new Element("td", {"class" : "valueName"}).insert(valueItem.name)).insert(new Element("td").insert("= " + valueItem.doc)));
                } else {
                  tbody.insert(new Element("tr", {"class" : "acse acmo"}).insert(new Element("td", {"class" : "valueName"}).insert(valueItem.name)).insert(new Element("td").insert("= " + valueItem.doc)));
                }
                counter++;
            });
        });
        
        cOffset = Element.cumulativeOffset(eventElement);

        aclist.setStyle({
          top: (cOffset[1] + eventElement.getHeight()).toPaddedString(0) + "px",
          left: cOffset[0].toPaddedString(0) + "px",
          position: "absolute"
        });

        aclist.show();
        
        $$('tr.acmo').each(function(element){
          Event.observe(element, 'mouseover', function(e){
            $$('tr.selected').each(function(element){
              element.removeClassName('selected');
            });
            element.addClassName('selected');
          });      
        });

        $$('tr.acse').each(function(element){
          Event.observe(element, 'click', function(e){
            valueToInsert = ""         
            $$('tr.selected').each(function(element){
                valueToInsert = element.down("td.valueName").innerHTML
            });
            eventElement.writeAttribute({value : valueToInsert});

            aclist = $('ac-list');
            aclist.innerHTML = "";
            aclist.hide();
          });
      });
	}
	
  // acof functionality for the project members
  projNameArray = $$('input[name="projectname"]');
  projName = "";
  if(projNameArray.size()>0){
      projName = projNameArray[0].readAttribute("value");
  }
  if(projName != ""){
  	urlProjectMembers = "/p/" + projName + "/feeds/projectMembers";
  	urlIssueOptions = "/p/" + projName + "/feeds/issueOptions"
	
  	new Ajax.Request(urlProjectMembers, {
  	  method: 'get',
  	  onSuccess: function(transport){
  	    $$('input.acofmember').each(function(element){
      		Event.observe(element, "focus", acofMemberHandler.bindAsEventListener(element, transport.responseText.evalJSON()));
      	});
    	
        // document.observe('click', function(e){
        //           aclist = $('ac-list');
        //           if(!Event.element(e).hasClassName('acofmember') && aclist.visible()){
        //             aclist.innerHTML = "";
        //             aclist.hide();
        //           }
        //         });
    	}
  	});
  	
  	new Ajax.Request(urlIssueOptions, {
  	  method: 'get',
  	  onSuccess: function(transport){
  	      json = transport.responseText.evalJSON();
  	      
  	      statusJSON = []
  	      statusJSON.push({'name' : 'Open', 'values' : json.open})
  	      statusJSON.push({'name' : 'Closed', 'values' : json.closed})
  	      
  	      $$('input.acofstatus').each(function(element){
  	          Event.observe(element, "focus", acofOptionsHandler.bindAsEventListener(element, statusJSON));
  	      });
  	      
  	      labelsJSON = []
  	      labelsJSON.push({'name' : 'Labels', 'values' : json.labels})
  	      
  	      $$('input.acoflabel').each(function(element){
  	          Event.observe(element, "focus", acofOptionsHandler.bindAsEventListener(element, labelsJSON));
  	      });
    	
    	}
  	});
	}
	
	// viewableInstructions functionality
	// Will show the instructions when the field is clicked on for that field.  Requires that the instructions already be 
	// written out on the page, and that there is a div tag with an id of instructions.
	
	function focusHelp(e){
        focusedElementId = e.element().identify();

        regexp = new RegExp(/^([a-zA-Z]+)([0-9]+)?$/);
        
        matches = regexp.exec(focusedElementId);

        if(matches != null && matches[2] != null){
        	focusedElementId = matches[1] + "2";
        }
        
        showInstructions(focusedElementId);
        
	}
	
	$$('.focusHelp').each(function(element){
	  Event.observe(element, "focus", focusHelp.bindAsEventListener(element));
	});
	
	function promptBoxSelection(e){
	    element = $('promptSelectionBox'); //select
	    optionValue = $F(element);
	    Form.Element.enable($('delete_prompt'));
	    promptAreaElement = $('promptarea');
	    promptAreaElement.removeClassName('undef');
	    
	    promptTextInputElement = $(optionValue);
	    
	    promptAreaElement.value = promptTextInputElement.readAttribute('value');
	}
	

    Event.observe($('promptSelectionBox'), "change", promptBoxSelection.bindAsEventListener($('promptSelectionBox')));
    
    function savePromptArea(e){
        promptAreaElement = $('promptarea');
        optionValue = $F('promptSelectionBox');
        promptTextInputElement = $(optionValue);

        promptTextInputElement.writeAttribute({value : promptAreaElement.value});
    }
    
    Event.observe($('promptarea'), "keyup", savePromptArea.bindAsEventListener($('promptarea')));
    
    function deletePrompt(e){
        r=confirm("Are you sure?");
        if(r==true){
            $(Event.element(e)).disable();
            promptAreaElement = $('promptarea');
            selectionBox = $('promptSelectionBox');
            optionValue = $F('promptSelectionBox');
            promptTextInputElement = $(optionValue);
            promptNameElement = $("name" + optionValue);
        
            selectionBox.childElements().each(function(element){
               if(element.selected){
                   element.remove();
               }
            });
            promptTextInputElement.remove();
            promptNameElement.remove();
            promptAreaElement.addClassName("undef");
            promptAreaElement.value = "Select prompt type from list.";
        }
    }
    
    Event.observe($('delete_prompt'), "click", deletePrompt.bindAsEventListener($('delete_prompt')));

    function createPrompt(e){

        body = $F('newTextPrompt');
        name = $F('newNamePrompt');
        type = $F('newTypePrompt');

        hiddenPrompts = $('hiddenPrompts');
        selectBox = $('promptSelectionBox');

        
        if(name.startsWith('User ')){
            name.sub("User ", "");
        } else if(name.startsWith('Developer ')){
            name.sub("Developer ", "");
        }
        
        name = type + " " + name;

        childElements = hiddenPrompts.childElements();
        if(childElements.size() > 0){
            nextPromptNumber = (childElements.last().readAttribute('promptnumber') * 1) + 1;
        } else {
            nextPromptNumber = 1;
        }

        hiddenPrompts.insert(newDiv = new Element('div', {promptnumber : nextPromptNumber}))
        
        newDiv.insert(new Element('input', {type :'hidden',
                                'id' : 'nameprompt'+nextPromptNumber.toString(),
                                'value' : name,
                                name : 'nameprompt'+nextPromptNumber.toString()}));
        newDiv.insert(new Element('input', {type : 'hidden',
                                'id' : 'prompt'+nextPromptNumber.toString(),
                                value : body,
                                name : 'prompt'+nextPromptNumber.toString()}));
        
        selectBox.insert(newOption = new Element('option', {value : 'prompt'+nextPromptNumber.toString()}).insert(name));
        
        newOption.selected = true;
        
        promptBoxSelection(null);
        
        hidePromptForm();
        
        Field.focus(selectBox);
        
    }
    
	Event.observe($('promptCreateButton'), "click", createPrompt.bindAsEventListener($('promptCreateButton')));
});