define [], ->
    # 表管理 
    ['$scope', '$resource', '$http', ($scope, $resource, $http)->
        actions =
            save: method: 'POST'
            update: method: 'PUT'
            mulit: method: 'GET', isArray: true

        Tables = $resource('/api/table', {}, actions)

        $scope.isList = true
        $scope.tables = Tables.mulit()

        # 存放表单定义
        _form_field = []

        # 取表单定义
        getFormField = (callback)->
            $http.get('/api/get.form', params: form: 'app.forms.cms.Table').
            success (data)->
                _form_field = data.form
                $scope.form = angular.copy _form_field
                if angular.isFunction callback
                    callback()

        getFormField()

        # 表单保存
        $scope.submit = ->
            postData = {}
            angular.forEach($scope.form, (field)->
                postData[field.name] = field.data
            )
            $scope.isList = true

            Tables.save(postData, (ret)->
                $scope.tables = Tables.mulit()
            )

        # 修改分类状态
        $scope.changeState = (val) ->
            data =
                id: val.id
                state: 0
            
            if val.state == 0
                data.state = 1

            Tables.update(data, (ret)->
                $scope.tables = Tables.mulit()
            )



        # 添加表单
        $scope.add = ->
            $scope.isList = false
            $scope.form   = angular.copy _form_field


        # 编辑表单
        $scope.edit = (val) ->
            $scope.isList = false
            $scope.form   = angular.copy _form_field

            angular.forEach $scope.form, (field)->
                # 不能更改模型
                if field.name == 'table'
                    field.disabled = true


                if val[field.name]
                    field.data = val[field.name]


    ]
