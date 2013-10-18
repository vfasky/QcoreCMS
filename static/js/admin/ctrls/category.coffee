define ['admin/directive'], (app)->
    app.controller('categoryCtrl' , ['$scope', '$resource', ($scope, $resource)->
        actions =
            mulit: method: 'GET', isArray: true

        Catgory = $resource('/api/category', {}, actions)

        $scope.catgorys = Catgory.mulit() 


        $scope.on_load_app_forms_cms_Category = (el)->
            console.log el

        return
    ])
    return
