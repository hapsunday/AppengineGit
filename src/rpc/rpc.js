rpc = {
		//_send = function(method, args, callback) {
		send: function(method, args) {
			var callback = rpc.writeResponse;
			/*
			 * private function which sends off the request and executes the callback upon recieving a response.
			 * This must not be called directly.
			 * 
			 * parameters:
			 * 	method (string): the name of the function to call
			 * 	args (object): javascript object with key value pairs. {argName:argValue,}
			 * 	callback (function): function with 3 parameters, (responseBody, httpStatusCode, xmlHttpRequestObj) 
			 */
			var ajax = new XMLHttpRequest();
			ajax.onreadystatechange = function() {
				if(ajax.readyState==4) {
					callback(ajax.responseText, ajax.status, ajax);
				}
			}
			ajax.open("POST", "/rpc/"+method, true);
			var query = "";
			for( key in args ) {
				query += "&";
				query += key;
				query += "=";
				query += args[key];
			}
			query = query.substr(1);
			ajax.send(query);
		},
		
		writeResponse: function(text, status, ajaxObj) {
			document.getElementById('response').innerHTML = status+'\n'+text;
		}
}