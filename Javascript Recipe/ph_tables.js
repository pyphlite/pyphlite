function populate_data(table_id, jdata, base_list) {
	//auto-populate keys
	var observed_keys = new Array();
	
	$.each(jdata[base_list], function(i, data_obj) {
		for (var k in data_obj) {
			if (observed_keys.indexOf(k) < 0) {
				observed_keys.push(k);
			}
		}
	});
	
	//print out the <thead> element
	keys_tr = "<tr>";
	$.each(observed_keys, function(i, k) {
		keys_tr += "<td>" + k + "</td>";
	});
	keys_tr += "</tr>"
	
	$(table_id).append("<thead>" + keys_tr + "</thead>");
	
	//print out the rows
	$.each(jdata[base_list], function(i, data_obj) {

		row_tr = "<tr>";
		$.each(observed_keys, function(i, k) {
		
			try {
				e = data_obj[k];
			} catch (err) {
				e = "";
			}
		
			row_tr += "<td>" + e + "</td>";
		});
		row_tr += "</tr>";
		
		$(table_id).append(row_tr);
	});
	
    $(table_id).DataTable();
}

function fill_table(table_id, json_url, base_list) {
	var xmlhttp = new XMLHttpRequest();
	
	xmlhttp.onreadystatechange = function() {
		if (xmlhttp.readyState == 4 && xmlhttp.status == 200) {
			var jdata = JSON.parse(xmlhttp.responseText);
			populate_data(table_id, jdata, base_list);
		}
	};
	xmlhttp.open("GET", json_url, true);
	xmlhttp.send();
};
