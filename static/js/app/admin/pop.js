define(function(require, exports, module) {
	var jQuery = require('jquery');
	var block  = require('./block');
	var Form   = require('YooYo/form');
	var win    = jQuery(window);


	require('jquery/easing')(jQuery);

	var pop = jQuery('<div class="ui-pop">'+
		             	'<div class="title"><span class="close">×</span><div class="in-wrap"></div></div>'+
		             	'<div class="content"></div>'+
		             '</div>');

	var title     = pop.find('.title .in-wrap');
	var close     = pop.find('.title .close');
	var content   = pop.find('.content');



	var callbacks = {
		onShow  : function(){},
		onHide  : function(){}
	};

	pop.hide().appendTo('body');

	exports.setTitle = function(dom){
		dom = dom instanceof jQuery ? dom : jQuery( '<div>' + dom + '</div>' );
		dom.appendTo(title.empty());
	};

	exports.setContent = function(dom){
		dom = dom instanceof jQuery ? dom : jQuery( '<div>' + dom + '</div>' );
		content.find('.in-wrap').remove();
		var wrap = jQuery('<div class="in-wrap"></div>');
		dom.appendTo(wrap);
		wrap.appendTo(content);
	};

	exports.centent = function(){
		pop.css({
			left : ( win.width() - pop.width() ) / 2
		});
	};

	exports.hide = function(){
		var top = pop.height() < 200 ? 200 : pop.height();
		pop.stop().animate({top : -top} , 'easeInOutQuint' , function(){
			callbacks.onHide();
			win.unbind('resize.ui-pop');
			block.hide();
			content.css({
				height : 'auto'
			});
			pop.hide();
		});
	};

	exports.show = function(args){
		args = jQuery.extend({
			width : 400 ,
			height : 'auto' ,
			title : '' ,
			content : '' ,
			zIndex  : 400 ,
			onShow  : function(){},
			onHide  : function(){}
		} , args || {});

		callbacks.onHide  = args.onHide;
		callbacks.onShow  = args.onShow;

		exports.setTitle(args.title);
		exports.setContent(args.content);

		pop.css({
			width : args.width ,
			height : args.height ,
			zIndex : args.zIndex
		});

		exports.centent();
		content.css({
			height : 'auto'
		});
		var time = setInterval(function(){
			var height = pop.height();

			if(height > 0){
				clearInterval(time);

				if( height > win.height() - 100){
					content.css({
						height : win.height() - 100
					});
				}
				

				var top = pop.height() < 200 ? 200 : pop.height();
				pop.css({top : - top}).show();

				win.unbind('resize.ui-pop')
				   .bind('resize.ui-pop',function(){
				   	  exports.centent();
				   });

				block.show();
				pop.stop().animate({top : 0} , 'easeInOutQuint' , function(){
					callbacks.onShow();
				});
			}
		},100);
		
	};

	exports.alert = function(msg,title){
		exports.show({
			title : title || '提示信息' ,
			content : '<div class="wrap">' + msg + '</div>'
		});
	};

	exports.form = function(title,config,data,callback){
		var dom = jQuery('<div class="ui-form"></div>');
		var form = new Form();
		form.loadConfig(config);
		form.build().appendTo(dom);

		form.setValues(data||{});

		if(callback){
			form.on('submit',function(){
				form.validate(callback);
				return false;
			})
		}

		exports.show({
			title : title || '' ,
			content : dom ,
			width : 490
		});

	};

	exports.conform = function(msg,callbacks,title){
		var dom = jQuery('<div><div class="wrap">'+msg+'</div></div>');
		dom.append('<div class="ui-form-actions"></div>');

		var okBtn = jQuery('<button class="ui-btn-large"><i class="icon-ok icon-white"></i>  确认</button> ');
		okBtn.appendTo(dom.find('.ui-form-actions'));

		var cancelBtn = jQuery('<button class="ui-btn-large"> 取消</button>');
		cancelBtn.appendTo(dom.find('.ui-form-actions'));


		cancelBtn.click(function(){
			exports.hide();
			return false;
		});

		okBtn.click(function(){
			exports.hide();
			callbacks();
			return false;
		});

		exports.show({
			title : title || '请确认' ,
			content : dom
		});

	};

	close.click(function(){
		exports.hide();
		return false;
	});
});