define [], ->
    # 表字段管理 
    ['$scope', '$resource', '$http', '$routeParams', '$window', 'Msg',
     ($scope, $resource, $http, $routeParams, $window, Msg)->
        table_id = $routeParams.id
        if not table_id
            $window.location.href = '#/content/table'

        actions =
            save: method: 'POST'
            update: method: 'PUT'
            mulit: method: 'GET', params: id: table_id

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
        
        # 保存数据
        $scope.submit = ->
            postData = {}
            angular.forEach($scope.form, (field)->
                postData[field.name] = field.data
            )
            postData.table_id = table_id

            console.log postData

            $scope.isList = true

            Fields.save(postData, (ret)->
                $scope.fields = Fields.mulit()
            )


        # 添加表单
        $scope.add = ->
            $scope.isList = false
            $scope.form   = angular.copy _form_field
            angular.forEach($scope.form, (field)->
                if field.name == 'table_id'
                    field.data = table_id
                    return false
            )
            
    ]
        
