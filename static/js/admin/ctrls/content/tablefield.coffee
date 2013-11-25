define [], ->
    # 表字段管理 
    ['$scope', '$resource', '$http', '$routeParams', '$window', 'Msg',
     ($scope, $resource, $http, $routeParams, $window, Msg)->
        id = $routeParams.id
        if not id
            $window.location.href = '#/content/table'

        actions =
            #save: method: 'POST'
            update: method: 'PUT'
            mulit: method: 'GET', params: id: id

        Fields = $resource("/api/tablefield", {}, actions)
        
        $scope.isList = true
        $scope.fields = Fields.mulit()
        
        # 修改label
        $scope.change = (v)->
            Fields.update v
        
        # 存放表单定义
        _form_field = []

        # 取表单定义
        getFormField = (callback)->
            $http.get('/api/get.form', params: form: 'app.forms.cms.TableField').
            success (data)->
                _form_field = data.form
                $scope.form = angular.copy _form_field
                if angular.isFunction callback
                    callback()

        getFormField()

        # 添加表单
        $scope.add = ->
            $scope.isList = false
            $scope.form   = angular.copy _form_field

            
    ]
        
