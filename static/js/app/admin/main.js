/*
  通用后台框架
 */
define(function(require, exports, module) {
	var jQuery = require('jquery');

	var Main = function(){
		var _header = jQuery('#header');
		var _menu   = jQuery('#menu');
		var _wrap   = jQuery('#wrap');
		var _main   = jQuery('#main');
		var _wif    = jQuery('#wrap-iframe');
		var _load   = _wrap.find('.loading');

		var _self = this;
		var _win  = jQuery(window);
		var _loadTime = false;

		this.setSize = function(){
			var height = _win.height() - _header.outerHeight();
			var width  = _win.width() - _menu.outerWidth();
			_menu.height( height );
			_wrap.css({
				width : width ,
				height : height ,
				top : _header.outerHeight() ,
				left : _menu.outerWidth()
			});
			_main.css({
				width : _win.width() ,
				height : _win.height()
			});
		};


		this.showLoad = function(){
			if(_loadTime) clearTimeout(_loadTime);
			_load.css({
				top : - _load.outerHeight() ,
				left : ( _wrap.width() - _load.outerWidth() ) / 2 
			});
			_loadTime = setTimeout(function(){
				_load.show()
				     .stop()
					 .animate({
					  	top : 0
					 });

				_loadTime = setTimeout(function(){
					_self.hideLoad();
				} , 5000);
			},300);

			
		};

		this.hideLoad = function(){
			if(_loadTime) clearTimeout(_loadTime);
			_load.stop().animate({
				top : - _load.outerHeight()
			} , function(){
				_load.hide();
			})
		};

		this.buidTitle = function(){
			var oldDom = false;
			_menu.find('.title').each(function(k){
				var spanDom = jQuery('<span>+</span>');
				var that    = jQuery(this);
				var dlDom   = _menu.find('dl').eq(k).hide();
				var isShow  = false;
				that.click(function(){
					if(false == isShow){
						isShow = true;
						spanDom.html('-');
						if(oldDom && oldDom != that) oldDom.click();
						oldDom = that;
						dlDom.show();
					}
					else{
						isShow = false;
						spanDom.html('+');
						dlDom.hide();
					}
					return false;
				});

				spanDom.appendTo(that);

				dlDom.find('dt').each(function(k1){
					var that    = jQuery(this);
					var spanDom = jQuery('<span>-</span>');
					var ddDom   = dlDom.find('dd').eq(k1);

					that.toggle(function(){
						spanDom.html('+');
						ddDom.hide();
					},function(){
						spanDom.html('-');
						ddDom.show();
					});

					ddDom.find('a').click(function(){
						_menu.find('a.select').removeClass('select');
						var url = jQuery(this).addClass('select').blur().attr('href');
						_self.showLoad();
						_wif.attr('src' , url);
						_wif.load(function(){
							_self.hideLoad();
						})
						
						return false;
					});

					spanDom.appendTo(that);
				})
			});
			_menu.find('.title').eq(0).click()
			_menu.find('a').eq(0).click();
		};

		this.init = function(){
			this.setSize();
			this.buidTitle();
			_win.resize(function(){
				_self.setSize();
			});

			
		};

		this.init();
	};

	return Main;
});