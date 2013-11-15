define [], ->
    # 分类管理
    ['$scope', '$resource', '$http', ($scope, $resource, $http)->
        actions =
            save: method: 'POST'
            update: method: 'PUT'
            mulit: method: 'GET', isArray: true

        Catgory = $resource('/api/category', {}, actions)

        $scope.isList   = true
        $scope.catgorys = Catgory.mulit()

        # 存放表单定义
        _form_field = []

        # 取表单定义
        getFormField = (callback)->
            $http.get('/api/get.form', params: form: 'app.forms.cms.Category').
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

            Catgory.save(postData, (ret)->
                $scope.catgorys = Catgory.mulit()
                getFormField ->
                    $scope.isList = true

            )

        # 修改分类状态
        $scope.changeState = (val) ->
             
            data =
                id: val.id
                state: 0
            
            if val.state == 0
                data.state = 1

            Catgory.update(data, (ret)->
                $scope.catgorys = Catgory.mulit()
            )
            
        # 编辑表单
        $scope.edit = (val) ->
            $scope.isList = false
            $scope.form   = angular.copy _form_field

            angular.forEach($scope.form, (field)->
                # 不能更改模型
                if field.name == 'table'
                    field.disabled = true

                # 限制不能选择自身，及下级
                else if field.name == 'parent'
                    fieldLevel = -1
                    ix = -1
                    removeCount = 1
                    isRemove = false
                    angular.forEach(field.choices, (v, k)->
                        level = $.trim(v.label).split('-').length - 1
                        if v.value.toString() == val.id.toString()
                            fieldLevel = level
                            isRemove = true
                            ix = k

                        else if level <= fieldLevel and fieldLevel != -1
                            isRemove = false

                        else if isRemove and fieldLevel != -1 and level > fieldLevel
                            removeCount = removeCount + 1

                    )

                    if ix != -1
                        field.choices.splice(ix, removeCount)
                     
                if val[field.name]
                    field.data = val[field.name]
            )


        # 添加表单
        $scope.add = ->
            $scope.isList = false
            $scope.form   = angular.copy _form_field

       
       
    ]
