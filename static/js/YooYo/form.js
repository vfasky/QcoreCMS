/**
 * @author vfasky@gmail.com
 */
define(function(require, exports, module) {
	var util   = require('./util');
	var jQuery = require('jquery');

	/**
	 * 验证规则
	 */
	var validators = function() {

		var isJson = function(str){
			json = jQuery.trim(str.toString());
			if('' == json) return {'success': true};
			try{
				jQuery.parseJSON(json);
				return {
	                'success': true
	            };
			}catch(e){
				return {
		            'success': false,
		            'msg': 'JSON格式错误'
		        };
			}
		}

	    /**
	     * 是否邮箱
	     * @param str
	     */
	    var isEmail = function(str) {
	        if (util.isEmail(str)) {
	            return {
	                'success': true
	            };
	        }
	        return {
	            'success': false,
	            'msg': '邮箱格式错误'
	        };
	    };

	    /**
	     * 是否数字
	     * @param str
	     */
	    var isNumber = function(str) {
	        if (util.isNumeric(str)) {
	            return { 
	                'success': true
	            };
	        }
	        return {
	            'success': false,
	            'msg': '只能为数字'
	        };
	    };

	    /**
	     * 是否网址
	     * @param str
	     */
	    var isUrl = function(str) {
	            var url = /^http:\/\/[A-Za-z0-9]+\.[A-Za-z0-9]+[\/=\?%\-&_~`@[\]\':+!]*([^<>\"\"])*$/;
	            var ret = url.test(str);

	            if (ret) {
	                return {
	                    'success': true
	                };
	            }
	            return {
	                'success': false,
	                'msg': '网址格式错误'
	            };
	        };

	    /**
	     * 不为空
	     * @param str
	     */
	    var notEmpty = function(str) {
	            if (false === util.isEmpty(str)) {
	                return {
	                    'success': true
	                };
	            }
	            return {
	                'success': false,
	                'msg': '不能为空'
	            };
	        };

	    return {
	        isEmail: isEmail,
	        isNumber: isNumber,
	        isUrl: isUrl,
	        notEmpty: notEmpty,
	        isJson: isJson
	    };
	}();

	/**
	 * 数据过滤
	 * @return {[type]} [description]
	 */
	var filters = function(){
	    var trim = function(str){
	        if(util.isString(str)){
	            return util.trim(str);
	        }
	        else if(util.isArray(str)){
	            var ret = [];
	            util.each(str , function(v,k){
	                ret[k] = trim(v);
	            });
	            return ret;
	        }
	    };

	    /**
	     * 转小写
	     * @param  {String||Array} o 如果是数组,只支持一维
	     * @return {String||Array}
	     */
	    var toLowerCase = function(str){
	        if(util.isString(str)){
	            return str.toLowerCase();
	        }
	        else if(util.isArray(str)){
	            var ret = [];
	            util.each(str , function(v,k){
	                ret[k] = toLowerCase(v);
	            });
	            return ret;
	        }
	    };

	    /**
	     * 转大写
	     * @param  {String||Array} o 如果是数组,只支持一维
	     * @return {String||Array}
	     */
	    var toUpperCase = function(str){
	        if(util.isString(str)){
	            return str.toUpperCase();
	        }
	        else if(util.isArray(str)){
	            var ret = [];
	            util.each(str , function(v,k){
	                ret[k] = toUpperCase(v);
	            });
	            return ret;
	        }
	    };

	    /**
	     * 转码html
	     * @param  {[type]} str [description]
	     * @return {[type]}     [description]
	     */
	    var escapeHTML = function(str){
	        return util.escapeHTML(str);
	    }

	    /**
	     * 转成数字
	     * @param  {[type]} str [description]
	     * @return {[type]}     [description]
	     */
	    var toNumber = function(str){
	        if(util.isNumeric(str)){
	            return Number(str);
	        }
	        else if(util.isArray(str)){
	            var ret = [];
	            util.each(str , function(v,k){
	                ret[k] = toNumber(v);
	            });
	            return ret;
	        }
	        return 0;
	    };

	    return {
	        trim : trim ,
	        toLowerCase : toLowerCase ,
	        toUpperCase : toUpperCase ,
	        escapeHTML : escapeHTML ,
	        toNumber : toNumber
	    }
	}();

	/**
	 * 表单元素基类
	 * @param {[type]} args  [description]
	 * @param {[type]} undef [description]
	 */
	var FormElementBase = function(args, undef){
		this.name       = args.name || '';
		this.label      = args.label || '';
		this.value      = args.value || '';
		this.attr       = args.attr || {};
		this.validators = args.validators || [];
	    this.filters    = args.filters || [];
	    this.data       = args.data || [];
	    this.type       = 'text';
	    this.dom        = false;
	    this.isPlugin   = false;

		/**
	     * 闭包
	     */
	    var _self = this;

	    this.elementDom =  function(){
	    	var html = '<input type="text" class="form-'+ this.type +'" name="'+ this.name +'"/>';

	    	var dom = jQuery(html);

	    	util.each(this.attr , function(v , k){
	    		dom.attr(k , v);
	    	});

	    	return dom;
	    };

	    this.buildDom = function(){
	    	this.dom    = jQuery('<div class="control-group"></div>');
	    	var label   = jQuery('<label class="control-label">'+ this.label +'</label>').appendTo( this.dom );
	    	var content = jQuery('<div class="controls"></div>').appendTo( this.dom );
	    	var tip     = jQuery('<span class="help-inline"></span>').hide().appendTo( content );

	    	this.dom.data('label' , label);
	    	this.dom.data('content' , content);
	    	this.dom.data('tip' , tip);

	    	jQuery.each(this.elementDom() , function(){
	    		jQuery(this).appendTo(content);
	    	});

	    	if(args.attr.tip){
	    		var tip = jQuery('<div class="tip"></div>').html(args.attr.tip).appendTo( content );
	    	}

	    	if('' != this.value){
				this.val(this.value)
			}
	    	return this.dom;
	    };

	    /**
	     * 设置或取得表单的值
	     * @param  {String||Array||undefined} val 要设置的值
	     * @return {String||Array||undefined}   
	     */
	    this.val = function(val){
	    	if(undef === val){
	    		this.value = this.dom.find('[name='+ this.name +']').val();
	    		//console.log(this.value)
	    		return this.value;
	    	}
	        //过滤
	        util.each(this.filters , function(v){
	            //console.log(filters)
	            if(filters.hasOwnProperty(v)){
	                val = filters[v](val);
	            }
	        });
	    	this.value = val;
	    	this.dom.find('[name='+ this.name +']').val(this.value);
	        return this.value;
	    };

	    /**
	     * 取配置
	     * @return {[type]} [description]
	     */
	    this.getConfig = function(){
	        return {
	            name : this.name ,
	            label : this.label ,
	            value : this.value ,
	            attr : this.attr ,
	            validators : this.validators ,
	            filters : this.filters ,
	            data : this.data ,
	            type : this.type
	        };
	    };

	    /**
	     * 发生错误时触发
	     * @param  {[type]} msg [description]
	     * @return {[type]}     [description]
	     */
	    this.onValidateError = function(msg){
	    	if(this.dom){
	    		this.dom.addClass('error').data('tip').html(msg).show();
	    	}
	        return msg;
	    };

	    this.on = function(event , callback){
	        var property = 'on' + util.ucfirst(event);
	        if(this.hasOwnProperty(property)){
	            this[property] = callback;
	        }
	    };

		/**
		 * 验证，成功后回调
		 * @param callback
		 */
		this.validate = function(callback) {
		    callback = callback || function() {};
		    var value = this.val();

		    var isPass = true;
	        
		    util.each(this.validators, function(v , k) {
		        if (validators.hasOwnProperty(v)) {
	                //console.log(v)

		            var ret = validators[v](value);
		            isPass = ret.success;
	                //console.log(ret)
		            if (false == isPass) {
		                _self.onValidateError(ret.msg);
		                return false;
		            }
		            else{
		            	if(_self.dom){
		            		_self.dom.removeClass('error').data('tip').hide();
		            	}
		            }
		        }
		    });
		    if (isPass) {
		        callback(value);
		    }
		};

	};

	/**
	 * 表单组件
	 */
	var formElements = {};

	/**
	 * 文本框
	 * @param {[type]} args [description]
	 */
	formElements.Text = function(args){
	    FormElementBase.call(this,args);
	};

	/**
	 * 图片上传
	 * @param {[type]} args [description]
	 */
	formElements.ImageUpload = function(args){
	    FormElementBase.call(this,args);
	    this.isPlugin   = true;
	    this.pluginType = 'ImageUpload';
	};

	


	/**
	 * 隐藏值
	 * @param {[type]} args [description]
	 */
	formElements.Hidden = function(args){
	    FormElementBase.call(this,args);
	    this.type = 'hidden';

	  
	    this.elementDom =  function(){
	    	var html =  '<input type="hidden" name="'+ this.name +'"/>';
	    	var dom = jQuery(html);

	    	util.each(this.attr , function(v , k){
	    		dom.attr(k , v);
	    	});

	    	return dom;
	    };

	    this.buildDom = function(){
	    	this.dom    = jQuery('<div class="control-group"></div>');
	    	var label   = jQuery('<label class="control-label">'+ this.label +'</label>').appendTo( this.dom );
	    	var content = jQuery('<div class="controls"></div>').appendTo( this.dom );
	    	var tip     = jQuery('<span class="help-inline"></span>').hide().appendTo( content );
	    	this.dom.data('label' , label);
	    	this.dom.data('content' , content);
	    	this.dom.data('tip' , tip);

	    	jQuery.each(this.elementDom() , function(){
	    		jQuery(this).appendTo(content);
	    	});

	    	if('' != this.value){
				this.val(this.value)
			}
	    	return this.dom.hide();
	    };
	};

	/**
	 * 密码框
	 * @param {[type]} args [description]
	 */
	formElements.Password = function(args){
	    FormElementBase.call(this,args);
	    this.type = 'password';

	    this.elementDom =  function(){
	    	var html =  '<input type="password" class="form-'+ this.type +'" name="'+ this.name +'"/>';
	    	var dom = jQuery(html);

	    	util.each(this.attr , function(v , k){
	    		dom.attr(k , v);
	    	});

	    	return dom;
	    };
	};

	/**
	 * 下拉框
	 * @param {[type]} args [description]
	 */
	formElements.Select = function(args , undef){
	    FormElementBase.call(this,args);
	    this.type = 'select';
	    
	    var _self = this;

	
	    this.elementDom =  function(){
	    	var html = '<select class="form-'+ this.type +'" name="'+ this.name +'">';

	    	util.each(this.data , function(v){
	    		html += '<option value="' + v.value + '">' + v.label + '</option>';
	    	})

	    	html += '</select>';

	    	var dom = jQuery(html);

	    	util.each(this.attr , function(v , k){
	    		dom.attr(k , v);
	    	});
	    	return dom;
	    };

	    /**
	     * 设置或取得表单的值
	     * @param  {String||Array||undefined} val 要设置的值
	     * @return {String||Array||undefined}   
	     */
	    this.val = function(val){
	        
	        if(undef === val){
	            return this.dom.find('[name='+ this.name +']').val();
	        }
	        
	        util.each(this.data , function(v){
	            if(util.isNumeric(val)) val = Number(val);

	            if(v.value === val){
	                _self.value = v.value;

	                return false;
	            }
	        });
	        this.dom.find('[name='+ this.name +']').val(this.value);
	        //console.log(this.value)

	        return this.value;
	    };
	};

	/**
	 * 单选框
	 * @param {[type]} args [description]
	 */
	formElements.Radio = function(args , undef){
	    FormElementBase.call(this,args);
	    this.type = 'radio';

	    var _self = this;

	    
	    this.elementDom =  function(){
	    	var html = '';

	    	util.each(this.data , function(v){
	    		html += '<label class="checkbox inline"><input class="form-radio" name="'+ _self.name +'" type="radio" value="' + v.value + '" >' + v.label + '</label>'; 
	    	});

	    	var dom = jQuery(html);

	    	util.each(this.attr , function(v , k){
	    		dom.attr(k , v);
	    	});

	    	return dom;
	    };

	    /**
	     * 设置或取得表单的值
	     * @param  {String||Array||undefined} val 要设置的值
	     * @return {String||Array||undefined}   
	     */
	    this.val = function(val){
	        if(undef === val){
	        	this.value = this.dom.find('[name='+ this.name +']:checked').val();
	            return this.value;
	        }
	   
	        util.each(this.data , function(v){
	            if(util.isNumeric(val)) val = Number(val);
	            if(v.value === val){
	                _self.value = v.value;
	                return false;
	            }
	        });
	        this.dom.find('input[value='+ this.value +']').attr('checked',true);

	        return this.value;
	    };
	};


	/**
	 * 复选框
	 * @param {[type]} args [description]
	 */
	formElements.Checkbox = function(args , undef){
	    FormElementBase.call(this,args);
	    this.type = 'checkbox';

	    var _self = this;

	    this.elementDom =  function(){
	    	var html = '';

	    	util.each(this.data , function(v){
	    		html += '<label class="checkbox inline"><input class="form-checkbox" name="'+ args.name +'" type="checkbox" value="' + v.value + '" >' + v.label + '</label>'; 
	    	})

	    	var dom = jQuery(html);

	    	util.each(this.attr , function(v , k){
	    		dom.attr(k , v);
	    	});

	    	return dom;
	    };

	    /**
	     * 设置或取得表单的值
	     * @param  {String||Array||undefined} val 要设置的值
	     * @return {String||Array||undefined}   
	     */
	    this.val = function(val){
	        if(undef === val){
	        	this.value = [];
	        	this.dom.find('[name='+ this.name +']:checked').each(function(){
	        		var that = jQuery(this);
	        		_self.value[_self.value.length] = that.val()
	        	})
	        	//console.log(this.value)
	            return this.value;
	        }
	        var attr = [];
	        util.each(this.data , function(v){
	        	util.each(val,function(_v){
	        		if(util.isNumeric(_v)) _v = Number(_v);
		            if(v.value === _v){
		            	_self.dom.find('input[value='+ v.value +']').attr('checked',true);
		                attr[attr.length] = v.value;
		            }
	        	})
	            
	        });
	        this.value = attr;

	        return this.value;
	    };
	};


	/**
	 * 多行文本
	 * @param {[type]} args [description]
	 */
	formElements.Textarea = function(args){
	    FormElementBase.call(this,args);
	    this.type = 'textarea';

	    this.elementDom =  function(){
	    	var html = '<textarea rows="3" name="'+ args.name +'" class="form-textarea"></textarea>';
	    	var dom = jQuery(html);

	    	util.each(this.attr , function(v , k){
	    		dom.attr(k , v);
	    	});

	    	return dom;
	    };

	    
	};

	/**
	 * 编辑器
	 * @param {[type]} args [description]
	 */
	formElements.Editor = function(args){
	    formElements.Textarea.call(this,args);
	    this.isPlugin   = true;
	    this.pluginType = 'Editor';
	};

	/**
	 * 组图
	 * * @param {[type]} args [description]
	 */
	formElements.Photos = function(args){
	    formElements.Textarea.call(this,args);
	    this.isPlugin   = true;
	    this.pluginType = 'Photos';
	};

	/**
	 * 视频
	 * * @param {[type]} args [description]
	 */
	formElements.Videos = function(args){
	    formElements.Textarea.call(this,args);
	    this.isPlugin   = true;
	    this.pluginType = 'Videos';
	};

	/**
	 * 按钮
	 * @param {[type]} args  [description]
	 */
	formElements.Button = function(args , undef){
		FormElementBase.call(this,args);
		this.type = args.type || 'submit';

		this.onValidateError = function(){};

		this.validate = function(callback){
			callback();
		};


		this.buildDom = function(){
	    	var dom  = jQuery('<button type="'+ this.type +'">'+ this.label +'</button>');
	    	
	    	util.each(this.attr , function(v , k){
	    		dom.attr(k , v);
	    	});

	    	return dom;
	    };
	};

	formElements.Submit = function(args , undef){
		FormElementBase.call(this,args);
		this.type = 'submit';

		this.onValidateError = function(){};

		this.validate = function(callback){
			callback();
		};


		this.buildDom = function(){
	    	var dom  = jQuery('<button type="'+ this.type +'">'+ this.label +'</button>');
	    	
	    	util.each(this.attr , function(v , k){
	    		dom.attr(k , v);
	    	});

	    	return dom;
	    };
	};


	var Form = function(action , method , enctype){
		this.action  = action || '';
		this.method  = method || 'POST';
		this.enctype = enctype || 'multipart/form-data';
		this.plugins = [];

	    /**
	     * 表单元素对象
	     * @type {Object}
	     */
	    var _elements = {};

	    /**
	     * 表单的值
	     * @type {Object}
	     */
	    var _values = {};

	    var _self = this;

	    var _isPass = false;

	    this.dom = jQuery('<form class="Yform" action="'+ this.action +'" method="'+ this.method +'" enctype="'+ this.enctype +'"></form>');

	    /**
	     * 对外发布插件接口
	     * @param  {[type]} type   [description]
	     * @param  {[type]} plugin [description]
	     * @return {[type]}        [description]
	     */
	    this.plugin = function(type,plugin){
	    	//console.log(this.plugins)
	    	util.each(this.plugins,function(e){
	    		if(e.pluginType == type){
	    			new plugin(e);
	    		}
	    	});
	    };

	    /**
	     * 构造表单dom
	     * @return {[type]} [description]
	     */
	    this.build = function() {
	    	var fieldsetDom = jQuery('<fieldset></fieldset>');
	    	var buttons = [];
	    	util.each(_elements , function(e){
	    		if(e.type != 'button' && e.type != 'submit'){
	    			e.buildDom().appendTo( fieldsetDom );
	    		}
	    		else{
	    			buttons[buttons.length] = e;
	    		}
	    	});

	    	this.dom.attr('action' , this.action);
	    	this.dom.attr('method' , this.method);
	    	this.dom.attr('enctype' , this.enctype);

	    	//console.log(_elements)

	    	fieldsetDom.appendTo( this.dom );
	    	//console.log(_elements)
	    	//加入button
	    	if(buttons.length > 0){
	    		var buttonsDom = jQuery('<div class="form-actions"></div>');
	    		util.each(buttons , function(b){
	    			b.buildDom().appendTo(buttonsDom);
	    		});
	    		//console.log(buttonsDom)
	    		buttonsDom.appendTo( this.dom );
	    	}

	    	this.dom.bind('submit' , function(){
	    		return _self.onSubmit();
	    	});

	    	return this.dom;
	    }

	    /**
	     * 添加组件
	     * @param {[type]} type [description]
	     * @param {[type]} args [description]
	     */
	    this.add = function(type , args){
	        type = util.ucfirst(type);
	        if( util.isString(args.name) && formElements.hasOwnProperty(type) ){
	            var element = new formElements[type](args);
	            _elements[args.name] = element;

	            if(element.isPlugin){
	            	_self.plugins[ _self.plugins.length ] = element;
	            	//console.log(_self.plugins)
	            }
	        }

	        return this;
	    };

	    /**
	     * 添加验证规则
	     * @param {[type]}   name     [description]
	     * @param {Function} callback [description]
	     */
	    this.addValidator = function(name , callback){
	        validators[name] = callback;
	    };

	    /**
	     * 添加过滤规则
	     * @param {[type]}   name     [description]
	     * @param {Function} callback [description]
	     */
	    this.addFilter = function(name , callback){
	        filters[name] = callback;
	    };

	    /**
	     * 设置表单的值
	     * @param {[type]} values [description]
	     */
	    this.setValues = function(values){
	        //console.log(_elements.sex.val);
	        util.each(values,function(v,name){
	            
	            if(_elements.hasOwnProperty(name)){
	                _elements[name].val(v);
	            }
	        });

	        return this;
	    };

	    /**
	     * 验证发生错误时触发
	     * @param  {FormElementBase} element 发生错误的表单元素
	     * @param  {String} msg     错误信息
	     */
	    this.onValidateError = function(){};

	    /**
	     * 提交事件
	     * @param  {[type]} values [description]
	     * @return {[type]}        [description]
	     */
	    this.onSubmit = function(values){
	    	//console.log(_isPass);
	    	if( false === _isPass){
	    		
	    		this.validate(function(){
	    			_self.onSubmit();
	    		})
	    	}
	    	return _isPass;
	    	
	    };

	    this.on = function(event , callback){
	        var property = 'on' + util.ucfirst(event);
	        if(this.hasOwnProperty(property)){
	            this[property] = callback;
	        }
	    };

	    /**
	     * 验证表单
	     * @param  {Function} callback [description]
	     * @return {[type]}            [description]
	     */
	    this.validate = function(callback){
	        callback = callback || function(){};
	        _isPass  = false;
	        _values = {};
	        var passCount  = 0;
	        var checkCount = 0;
	        util.each(_elements,function(e){

	            // e.on('validateError' , function(msg){
	            //     //console.log(msg)
	            //     _self.onValidateError(e, msg);
	            // });
	        	if(e.type != 'submit'){
	        		e.validate(function(val){
		                passCount++;
		                _values[e.name] = val;
		            });
		            checkCount++;
	        	}
	            
	        });
	        //验证通过
	        if( passCount ===  checkCount)
	        {
	        	_isPass = true;
	            callback(_values);
	        }
	        else{
	        	_self.onValidateError();
	        }
	    };

	    /**
	     * 取表单的配置
	     * @return {[type]} [description]
	     */
	    this.getConfig = function(){
	        var config = {
	            action : this.action ,
	            method : this.method ,
	            enctype : this.enctype ,
	            elements : []
	        };

	        util.each(_elements,function(e){
	            config.elements[ config.elements.length ] = e.getConfig();
	        });

	        return config;
	    };

	    this.loadConfig = function(config){
	    	this.action = config.action;
	    	this.method = config.method;
	    	this.enctype = config.enctype;

	    	util.each(config.elements,function(v){
	    		_self.add(v.type,v);
	    	});
	    };
	};

	return Form;
});