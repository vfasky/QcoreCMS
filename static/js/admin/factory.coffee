define ['jQuery', 'angular', 'bootstrap'], ($, angular)->
    
    class Modals
        _tpl = '
            <div class="modal fade" role="dialog" aria-hidden="true">
              <div class="modal-dialog">
                <div class="modal-content">
                  <div class="modal-header">
                    <button type="button" data-dismiss="modal" aria-hidden="true" class="close">&times;</button>
                    <h4 class="modal-title"></h4>
                  </div>
                  <div class="modal-body"></div>
                  <div class="modal-footer"></div>
                </div><!-- /.modal-content -->
              </div><!-- /.modal-dialog -->
            </div><!-- /.modal -->
        '

        constructor: (@body='', @title='', @footer='') ->
            @el = $ _tpl

    
        # 设置dom
        setDom: (selectName, target) ->
            selectEl = @el.find selectName
            if angular.isString target
                selectEl.html target

            else if angular.isFunction(target.appendTo)
                target.appendTo selectEl

            selectEl

        setTitle: (title) ->
            @setDom('.modal-title', title)

        setBody: (body) ->
            @setDom('.modal-body', body)

        setFooter: (footer) ->
            @setDom('.modal-footer', footer)


        # 提示窗
        alert: (@body, callback=->) ->
            @el = $ _tpl
            @footer = $ '<button type="button" data-dismiss="modal" class="btn btn-primary">确定</button>'

            @setTitle '提示信息'
            @setBody @body
            @setFooter @footer

            @el.modal(
                backdrop: false
            )
            @el.on('hidden.bs.modal', =>
                @el.remove()
                callback()
                
                return
            )
            @el

        # 确认窗
        confirm: (@body, callback=->) ->
            @el = $ _tpl
            @footer = $ '
                <button type="button" data-dismiss="modal" class="btn btn-default">取消</button>

                <button type="button" role="yes" data-dismiss="modal" class="btn btn-primary">确定</button>
            '

            @setTitle '提示信息'
            @setBody @body
            @setFooter @footer

            ret = false
            @el.on('click', '[role=yes]', ->
                ret = true
            )

            @el.modal(
                backdrop: false
            )
            @el.on('hidden.bs.modal', =>
                @el.remove()
                callback(ret)
                
                return
            )
            @el
    
    angular.module('admin.factory', [])
           .factory('Modals', ->
                new Modals()
           )

