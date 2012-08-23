define(function(require, exports, module) {
	var jQuery = require('jquery');
	
	exports.render = function(){
		jQuery('.ui-table-un,.ui-table').each(function(){
			var that = jQuery(this);

			that.find('tr:even').addClass('old');

			that.find('tr').hover(function(){
				jQuery(this).addClass('hover');
			},function(){
				jQuery(this).removeClass('hover');
			});
		});
	};
});