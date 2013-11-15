require.config
    baseUrl: '/static/js'
    paths:
        'jQuery': '//dn-staticfile.qbox.me/jquery/2.0.3/jquery.min'
        'bootstrap': '//dn-staticfile.qbox.me/twitter-bootstrap/3.0.0/js/bootstrap.min'
        'angular': '//dn-catke.qbox.me/js/angular-1.2.0/angular.min'
        'angularResource': '//dn-catke.qbox.me/js/angular-1.2.0/angular-resource.min'
        'angularRoute': '//dn-catke.qbox.me/js/angular-1.2.0/angular-route.min'
        'angularMocks': '//dn-catke.qbox.me/js/angular-1.2.0/angular-mocks'
        'adminRoutes': '/admin/js/routes'
        'adminControllers': '/admin/js/controllers'
    shim:
        'angular' : {'exports' : 'angular'}
        'jQuery': {'exports' : 'jQuery'}
        'bootstrap': { deps:['jQuery'] }
        'angularResource': { deps:['angular']}
        'angularRoute': ['angular'],
        'angularMocks':
            deps:['angular'],
            'exports':'angular.mock'
    priority: ["angular"]


require ['angular', 'admin/app', 'jQuery', 'adminRoutes'], (angular, app, $) ->
    'use strict'

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


    $html = angular.element document.getElementsByTagName('html')[0]

    angular.element().ready ->
        $html.addClass('ng-app')
        angular.bootstrap($html, [app['name']])

return
    
