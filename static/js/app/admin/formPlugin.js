define(function(require, exports, module) {
	var jQuery = require('jquery');
	var JSON   = require('json');
	var pop    = require('./pop');

	//视频列表
	exports.vidoesPlugin = function(e){
		var textarea = e.dom.find('textarea').hide();
		var data = jQuery.parseJSON(textarea.val()) || [];
		var list = [];
		

		var addBtn = jQuery('<button type="button" class="ui-btn"><i class="icon-facetime-video"></i> 添加</button>').appendTo(e.dom.find('.controls'));

		var video = function(v){
			var dom = jQuery('<div class="form-photos"></div>');
			dom.append('<input type="text" class="form-text" value="'+ (v.url || '')+'"/>');
			
			dom.append('<button type="button" class="ui-btn act-info">描述</button>');
			dom.append('<button type="button" class="ui-btn act-del"><i class="icon-trash"></i></button>');
			dom.append('<div class="video"></div>');
			dom.appendTo(e.dom.find('.controls'));
			var that = this;

			var input = dom.find('.form-text');
			var videoDom = dom.find('.video').css({
				position : 'absolute',
				left : 4 ,
				top : - 315 ,
				width : 420 ,
				height : 315
			});
			var time = false;
			var info = false;

			input.add(videoDom).hover(function(){
				if(time) clearTimeout(time);
				time = setTimeout(function(){
					if( videoDom.html() != '' ) return videoDom.show();
					if( input.val().toString().indexOf('//youtu.be/') != -1 ){
						var arr = input.val().split('//youtu.be/');
						if(arr.length==2){
							videoDom.html('<iframe width="420" height="315" src="http://www.youtube.com/embed/'+arr[1]+'?rel=0" frameborder="0" allowfullscreen></iframe>')
						}
					};
				},300);
				
			},function(){
				if( time) clearTimeout(time);
				time = setTimeout(function(){
					videoDom.hide();
				}, 500)
			});

			dom.find('.act-info').click(function(){
				pop.form('添加描述',{ elements : [
					{
						'type' : 'text' ,
						'name' : 'title' ,
						'label' : '标题' ,
						'attr' : {}
					},
					{
						'type' : 'textarea' ,
						'name' : 'info' ,
						'label' : '简介' ,
						'attr' : {}
					},
					{
						'type' : 'submit' ,
						'name' : 'send' ,
						'label' : '保存' ,
						'attr' : {}
					}
				]},v,function(val){
					//console.log(val)
					info = val;
					pop.hide();
					return false;
				});
				return;
			});

			dom.find('.act-del').click(function(){
				//console.log(list);
				pop.conform('确认删除? ' , function(){
					jQuery.each(list,function(k,v){
						if(v == that){
							list.splice(k,1);
							//console.log(list);
							dom.remove();
							return false;
						}
					});
				})
				return false;
			});

			this.getValue = function(){
				if (input.val() == '') return false;
				return {
					'url' : input.val() ,
					'title' : info ? info['title'] : '' ,
					'info' : info ? info['info'] : ''
				}
			};
		};

		addBtn.click(function(){
			list[ list.length ] = new video({});
			return false;
		})

		jQuery.each(data,function(k,v){
			list[ list.length ] = new video(v);
		});

		e.val = function(){
			var data = [];
			jQuery.each(list,function(k,v){
				var val = v.getValue();
				if(val){
					data[ data.length ] = val;
				}
			});
			var json = JSON.stringify(data);
			return json;
		};
	};

	//组图插件
	exports.photosPlugin = function(e){
		var textarea = e.dom.find('textarea').hide();
		var data = jQuery.parseJSON(textarea.val()) || [];
		var list = [];

		var updataDom = jQuery('<div><input type="button" value="上传" /></div>').appendTo(e.dom.find('.controls'));

		var uploadbutton = KindEditor.uploadbutton({
			button : updataDom.find('input')[0],
			fieldName : 'fileData',
			url : '/admin/uploadFile',
			afterUpload : function(data) {
				if (data.error === 0) {
					var url = KindEditor.formatUrl(data.url, 'absolute');
					list[ list.length ] = new buildList(data);
				} else {
					pop.alert(data.message);
				}
			},
			afterError : function(str) {
				pop.alert('服务器返回异常');
			}
		});
		uploadbutton.fileBox.change(function(e) {
			uploadbutton.submit();
		});

		var buildList = function(v){
			var that = this;
			v.title = v.fileName || v.title;
			var dom = jQuery('<div class="form-photos-item"></div>');
			dom.append('<img src="'+ v.url +'" width="120" height="90" alt=""/>');
			dom.append('<button type="button" class="ui-btn act-del"><i class="icon-trash"></i></button>');
			var info = false;

			dom.hover(function(){
				dom.find('.act-del').show();
			},function(){
				dom.find('.act-del').hide();
			});

			dom.find('.act-del').click(function(){
				pop.conform('确认删除? ' , function(){
					jQuery.each(list,function(k,v){
						if(v == that){
							list.splice(k,1);
							//console.log(list);
							dom.remove();
							return false;
						}
					});
				});
				return false;
			});

			dom.find('img').click(function(){
				pop.form('添加描述',{ elements : [
					{
						'type' : 'text' ,
						'name' : 'title' ,
						'label' : '标题' ,
						'attr' : {}
					},
					{
						'type' : 'textarea' ,
						'name' : 'info' ,
						'label' : '简介' ,
						'attr' : {}
					},
					{
						'type' : 'submit' ,
						'name' : 'send' ,
						'label' : '保存' ,
						'attr' : {}
					}
				]}, info ||　v,function(val){
					//console.log(val)
					info = val;
					pop.hide();
					return false;
				});
				return;
			});

			dom.appendTo(e.dom.find('.controls'));

			this.getValue = function(){
				return {
					'url' : v.url ,
					'title' : info ? info['title'] : v.title ,
					'info' : info ? info['info'] : ''
				}
			};
		};

		jQuery.each(data,function(k,v){
			list[ list.length ] = new buildList(v);
		});


		e.val = function(){
			var data = [];
			jQuery.each(list,function(k,v){
				data[ data.length ] = v.getValue()
			});
			var json = JSON.stringify(data);
			return json;
		};	
	};

	//图片上传插件
	exports.imageUploadPlugin = function(e){

		var input = e.dom.find('input').hide();
		
		var upBtn = jQuery('<input type="button" value="上传" />');
		var txt = jQuery('<div class="form-imageUpload"></div>').appendTo(e.dom.find('.controls'));
		upBtn.appendTo(e.dom.find('.controls'));

		var _url = e.val() == '' ? false : e.val();

		if(_url){
			txt.html('<img src="' + _url + '" alt="" width="120" height="90" />')
		}

		var uploadbutton = KindEditor.uploadbutton({
			button : upBtn[0],
			fieldName : 'fileData',
			url : '/admin/uploadFile',
			afterUpload : function(data) {
				if (data.error === 0) {
					var url = KindEditor.formatUrl(data.url, 'absolute');
					input.val(url);
					txt.html('<img src="' + url + '" alt="" width="120" height="90" />')
					_url = url;
				} else {
					pop.alert(data.message);
				}
			},
			afterError : function(str) {
				pop.alert('服务器返回异常');
			}
		});
		uploadbutton.fileBox.change(function(e) {
			uploadbutton.submit();
		});
	};
	
	//编辑器插件
	exports.editorPlugin = function(e){
		dom = e.dom.find('textarea');
		dom.height(400);
		var editor = KindEditor.create(dom[0], {
				resizeType : 1,
				themeType : 'simple',
				allowPreviewEmoticons : false,
				uploadJson : '/admin/uploadFile' ,
				filePostName : 'fileData' ,
				allowImageUpload : true ,
				allowFlashUpload : false ,
				items : ['source', '|', 'undo', 'redo', '|', 'preview', 'print', 'cut', 'copy', 'paste',
    'plainpaste', 'wordpaste', '|', 'justifyleft', 'justifycenter', 'justifyright',
    'justifyfull', 'insertorderedlist', 'insertunorderedlist', 'indent', 'outdent', 'subscript',
    'superscript', 'clearhtml', 'quickformat', 'selectall', '|', 'fullscreen', '/',
    'formatblock', 'fontname', 'fontsize', '|', 'forecolor', 'hilitecolor', 'bold',
    'italic', 'underline', 'strikethrough', 'lineheight', 'removeformat', '|', 'image', 
    'flash',  'insertfile', 'table', 'hr', 
    'anchor', 'link', 'unlink']
			});

        //重写
		e.val = function(val,undef){
			if(val==undef){
				return editor.html();
			}
			editor.html(val);
		};
	};
});