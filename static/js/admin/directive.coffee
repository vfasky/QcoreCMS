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

    app.directive('loadForm', ['$http', '$compile', ($http, $compile)->
        (scope, element, attr) ->
            formName = attr.loadForm
            el       = $(element)

            el.removeAttr('load-form')

            $http.get("/admin/form?form=#{formName}").success (formHtml)->
                el.html formHtml
                $compile(el)(scope)
                callbackName = 'on_load_' + formName.replace(/\./g, '_')
                console.log callbackName
                if $.isFunction scope[callbackName]
                    scope[callbackName](el)
    ])

    return app
