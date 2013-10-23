define ['admin/directive'], (app)->
    app.controller('categoryCtrl' , ['$scope', '$resource', '$http',
    ($scope, $resource, $http)->
        actions =
            save: method: 'POST'
            mulit: method: 'GET', isArray: true

        Catgory = $resource('/api/category', {}, actions)

        $scope.isList   = true
        $scope.catgorys = Catgory.mulit()

        
        $scope.onSubmitAppFormsCmsCategory = ->
            formEl   = this.formEl
            postData = {}

            formEl.find('[name]').each ->
                self = $ this
                postData[self.attr('name')] = self.val()

            Catgory.save(postData, ->
                $scope.isList   = true
                $scope.catgorys = Catgory.mulit()
            )

            
        $scope.onLoadAppFormsCmsCategory = (el)->
            formEl = el.find('form')

            $scope.formEl = formEl

            # 编辑表单
            $scope.edit = (val) ->
                $scope.isList = false

                formEl.find('[name]').each ->
                    self = $ this
                    if val[self.attr('name')]
                        self.val val[self.attr('name')]

            return

    ])
    return
