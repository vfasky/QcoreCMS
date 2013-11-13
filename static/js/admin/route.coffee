define ['admin/provider'], (app)->

    app.config ['$httpProvider', 'MsgProvider'
      ($httpProvider, MsgProvider)->
        $httpProvider.defaults.headers.post['Content-Type'] = 'application/x-www-form-urlencoded'

        $httpProvider.defaults.transformRequest = (data) ->
            $.param data ? {}

        $httpProvider.defaults.transformResponse = (data, headersGetter) ->
            if headersGetter()['content-type'].indexOf('json') != -1
                json = angular.fromJson data
                if json.success
                    return json.data
                else
                    MsgProvider.$get().error json.msg
                    #console.log json.msg
                    return null
            else
                return data
        
    ]
    
    app
    
