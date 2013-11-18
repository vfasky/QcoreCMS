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
            
    ]
        
