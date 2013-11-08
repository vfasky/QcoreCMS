require ['jQuery', 'angular', 'admin/route'], ($, angular, app)->
    #TODO 加入后台首页
    ctrls = []
    routes = []

    # 菜单事件
    $ ->
        el = $ '[admin-menu]'
        el.on 'click', 'a[data-toggle], a[avatar]', ->
            el.find('li.active').removeClass('active')
            $(this).parent().addClass('active')

        el.find('li.dropdown').each ->
            self = $ this
            if self.find('li').length == 0
                self.remove()
        return

    $.getJSON '/api/admin.route', (json)->
        if false == json.success
            alert json.msg
            return

        for v in json.data.routes
            ctrls.push v.js
            routes.push v

        # 动态加载路由
        require ctrls, ->
            app.config ['$routeProvider', ($routeProvider) ->

                for v in routes
                    $routeProvider.when(v.uri,
                        controller: v.name,
                        templateUrl: v.tpl
                    )
            ]
            
            angular.bootstrap(document , ['adminApp'])
            
            return

        return

    return
 
