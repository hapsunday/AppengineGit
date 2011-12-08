$.ajaxSetup({
	url: '/rpc/',
	type: 'POST',
	dataType: 'json',
	success: function(data, textStatus, jqXHR) {
		console.log(data, textStatus, jqXHR);
	},
	error: function(jqXHR, textStatus, errorThrown) {
		console.log(jqXHR, textStatus, errorThrown);
	}
});
$(document).ajaxSend(function(event, jqXHR, ajaxOptions){
	//set the correct url
	ajaxOptions.url = '/rpc/'+ajaxOptions.method;
});

Toolbar = {
	add: function(text) {
		var element = $('<button>'+text+'</button>')
		element.button();
		element.appendTo('#toolbar');
		return element
	},
	clear: function() {
		$('#toolbar').children().remove();
	},
};
Repositories = {
	_element: '#repositories',
	_repos: [],
	init: function() {
		$('.repo').live({
			mouseenter: function(){
				$(this).addClass('ui-state-focus');
			},
			mouseleave: function(){
				$(this).removeClass('ui-state-focus');
			},
		});
		Repositories.fetch();
	},
	fetch: function() {
		$.ajax({
			method: 'repo.list',
			success: function(data, textStatus, jqXHR) {
				Repositories._repos = data;
				Repositories.list_all();
			},
		});
	},
	clear: function() {
		$(Repositories._element).children().remove();
	},
	list: function(repo) {
		var ele = $('<li><div class="repo ui-state-default"><span class="name">'+repo.name+'</span></div></li>');
		$(ele).appendTo($(Repositories._element));
	},
	list_all: function() {
		Repositories.clear();
		for( repo in Repositories._repos ) {
			Repositories.list(Repositories._repos[repo]);
		}
	},
	create: function(repoName) {
		$.ajax({
			method: 'repo.create',
			data: 'name='+repoName,
			success: function(data, textStatus, jqXHR) {
				Repositories.fetch();
			},
			error: function(jqXHR, textStatus, errorThrown) {
				console.log('error with ajax', errorThrown);
				alert('error creating repo, check javascript console');
			}
		})
	},
	remove: function() {
		//not implemented server side
	},
};

$(document).ready(function(){
	Toolbar.add('Create Repository').bind({
		click: function() {
			$('#create_repo').dialog('open');
		},
	});
	Repositories.init();
	
	//set up dialogs
	$('#create_repo').dialog({
		title: "Create Repository",
		autoOpen: false,
		modal: true,
		resizable: false,
		draggable: false,
		width: 600,
		height: 400,
		buttons: {
			'Create': function(){
				Repositories.create(document.forms.create_repo.name.value);
				$(this).dialog('close');
			},
			'Cancel': function(){
				$(this).dialog('close');
			},
		}
	}).tabs();
});