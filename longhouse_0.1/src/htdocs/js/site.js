function _toggleStarLocal(element, element_type) {
	if(element_type == 'star') {
		var src_img = element.getAttribute('src');
		if(src_img == '/images/star_on.gif') {
			element.setAttribute('src', '/images/star_off.gif');
			document.getElementById('star').setAttribute('value', "0");
		} else {
			element.setAttribute('src', '/images/star_on.gif');
			document.getElementById('star').setAttribute('value', "1");
		}  		
	 }
}

function _toggleStar(element, project_name, issue_id){
    urlStarToggle = "/p/" + project_name + "/issues/setstar.do"
    
    var src_img = element.getAttribute('src');
    var is_starred;
    if(src_img == '/images/star_on.gif'){
        is_starred = 0
    } else {
        is_starred = 1
    }
    
    new Ajax.Request(urlStarToggle, {
  	  method: 'post',
  	  parameters: {issueid : issue_id, starred : is_starred},
  	  onSuccess: function(transport){
	      json = transport.responseText.evalJSON();
	      if(json.star == 1){
	          element.writeAttribute({src : '/images/star_on.gif'})
	      } else {
	          element.writeAttribute({src : '/images/star_off.gif'})	          
	      }
      }
      
    });
}

function _showInsteadFinal(divid, linkid){
  if(document.getElementById(divid).style.display == 'none'){
    document.getElementById(divid).style.display = '';
    document.getElementById(linkid).style.display = 'none';
  }else{
    document.getElementById(divid).style.display = 'none';
    document.getElementById(linkid).style.display = '';
  }
}

function _showInstead(divid, nextlinkid, thislinkid){
  if(document.getElementById(divid).style.display == 'none'){
    document.getElementById(divid).style.display = '';
    document.getElementById(nextlinkid).style.display = '';
    document.getElementById(thislinkid).style.display = 'none';
  }else{
    document.getElementById(divid).style.display = 'none';
    document.getElementById(nextlinkid).style.display = 'none';
    document.getElementById(thislinkid).style.display = '';
  }
}

function _exposeExistingLabelFields(divid) {
	for(i = 2;i<5;i++){
		concatDivId = divid + "row" + i;
		divEle = document.getElementById(concatDivId);
		inputTags = divEle.getElementsByTagName("input");
		
		if(inputTags[inputTags.length - 1].value != '') {
			nextLinkId = "addrow" + (i + 1);
			thislinkid = "addrow" + i;
			_showInstead(concatDivId, nextLinkId, thisLinkId);
		}
	}
	
}

function _showID(divid){
	document.getElementById(divid).style.display = '';
}

function _hideID(linkid){
	document.getElementById(linkid).style.display = 'none';
}

function highlightInstruction(inputObject) {
	id = inputObject.id;
	regexp = new RegExp(/^([a-zA-Z]+)([0-9]+)?$/);
	matches = regexp.exec(id);
	if(matches != null && matches[2] != null){
		id = matches[1];
	}
	inputObject.setAttribute("oldStyle", inputObject.getAttribute("style"));
	inputObject.style.background = "yellow";
	document.getElementById(id + "instructions").setAttribute("oldStyle", document.getElementById(id + "instructions").getAttribute("style"));
	document.getElementById(id + "instructions").style.background = "yellow";
	document.getElementById(id + "instructions").style.padding = "2px";
	
}

function removeHighlight(inputObject) {
	id = inputObject.id;
	regexp = new RegExp(/^([a-zA-Z]+)([0-9]+)?$/);
	matches = regexp.exec(id);
	if(matches != null && matches[2] != null){
		id = matches[1];
	}
	inputObject.setAttribute("style", inputObject.getAttribute("oldStyle"));
	document.getElementById(id + "instructions").setAttribute("style", document.getElementById(id + "instructions").getAttribute("oldStyle"));
}

function _clearOnFirstEvent(){
	sum = document.getElementById("summary");
	if(sum.value == "Enter one-line summary") {
		sum.value = "";
	}
}

function showInstructions(id){
  regexp = new RegExp(/^([a-zA-Z]+)([0-9]+)?$/);
	matches = regexp.exec(id);
	if(matches != null && matches[2] != null){
		id = matches[1];
	}
	
	instructionId = id + "instructions";
	
  $('instructions').nextSiblings().each(function(element){
    element.hide();
  });
  
  $(instructionId).show();
  $('instructions').scrollTo();
}

var fileAttachmentCount = 1;

function _addAttachmentFields(idToAddTo){
    $('attachafile').innerHTML = "Attach another file"
    
    elementToAddTo = $(idToAddTo);
    elementToAddTo.setStyle({margin:"0 0 0 4px"});
    elementToAdd = new Element('div');
    elementToAdd.insert(new Element("input", {type:"file", name:"file" + fileAttachmentCount, style:"width: auto; margin-left: 17px;", size:"35"}));
    elementToAdd.insert(new Element("a", {onclick:"this.parentNode.parentNode.removeChild(this.parentNode); return false", href:"#", style:"margin-left:3px;font-size: x-small;"}).insert("Remove"));
    
    elementToAddTo.insert(elementToAdd);
    
    fileAttachmentCount++;
}

function _acmo(event){}

function _onload(){}

function _fetchOptions(projectId, optionsToGrab){}

function _forceProperTableWidth(){}

function _acof(event){}

function _vallab(element){}

function _dirty(){}

function _confirmNovelStatus(element){}

function _RC(element, event){}