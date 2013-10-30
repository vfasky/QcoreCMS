define ['jQuery', 'admin/app', 'bootstrap'], ($, app)->
   
    app.directive('toolTip', [ ->
        (scope, element, attr) ->
            tip       = attr.toolTip
            placement = attr.placement ? 'top'
            trigger   = attr.trigger ? 'hover'
            el        = $(element)

            el.tooltip
                placement: placement
                trigger: trigger
                title: tip

    ])

    app.directive('loadForm', ['$http', '$compile', '$timeout', ($http, $compile, $timeout)->
        (scope, element, attr) ->
            formName = attr.loadForm
            el       = $(element)

            el.removeAttr('load-form')

            $http.get("/admin/form?form=#{formName}").success (formHtml)->
                #actionName = formName.replace(/\./g, '_')
                actions     = formName.split('.')
                actionNames = []
                formName    = false
                $.each(actions, (k, v) ->
                    actionNames.push v.toLowerCase().replace(/(?=\b)\w/g, (e) ->
                        e.toUpperCase()
                    )
                )
                actionName = actionNames.join('')

                el.html(formHtml)
                # 表单提交时的处理函数
                submitAction = "onSubmit#{actionName}"

                if $.isFunction scope[submitAction]
                    el.find('form').attr('ng-submit', "#{submitAction}()")

                if scope["_#{actionName}Name"]
                    formName = scope["_#{actionName}Name"]

                    el.find('form').attr('name', formName)

                    el.find('.form-group').each ->
                        groupEl = $(this)
                        nameEl = groupEl.find('[required]')
                        #console.log nameEl
                        if nameEl.length > 0
                            inputName = nameEl.eq(0).attr('name')
                            errEl = $ "<div class=\"alert alert-danger\" ng-show=\"#{formName}.#{inputName}.$error.required\">Required!</div>"
                            nameEl.after errEl

                $compile(el)(scope)

                callbackName = 'onLoad' + actionName

                if $.isFunction scope[callbackName]
                    $timeout(->
                        scope[callbackName](el)
                    , 0)
    ])

    return app
