define(function(require, exports, module) {
	var jQuery = require('jquery');
	var block  = jQuery('<div class="ui-block"></div>').hide().appendTo('body');
	var win    = jQuery(window);

	exports.dom = block;

	exports.setSize = function(){
		var bodyHeight = jQuery('body').height();
		var winHeight  = win.height();
		block.css({
			width : win.width() ,
			height : winHeight > bodyHeight ? winHeight : bodyHeight
		});
	};

	exports.show = function(args){
		args = jQuery.extend({
			opacity : .1 ,
			background : '#000' ,
			zIndex : 300
		} , args || {});

		win.unbind('resize.ui-block')
		   .bind('resize.ui-block',function(){
		   	  exports.setSize();
		   });

		exports.setSize();

		block.css(args).show();
	};

	exports.hide = function(){
		block.hide();
	};
});