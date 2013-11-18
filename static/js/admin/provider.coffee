define ['jQuery', 'angular', 'bootstrap'], ($, angular)->
    
    _msgWrapEl = $ '
        <div class="row"><div class="col-md-4 col-md-offset-4 msg-el"></div></div>
    '
    _msgEl = _msgWrapEl.find('.msg-el')

    _msgWrapEl.css
        zIndex: 1500

    _msgEl.css
        position: 'relative'

    $ -> _msgWrapEl.prependTo 'body'


    angular.module('admin.provider', [])
           .factory('Msg', ->
                Msg = {}

                Msg.pushMsg = (msg, type='warning') ->
                    el = $ "
                    <div class=\"alert alert-#{type}\">
                        <button type=\"button\" data-dismiss=\"alert\" aria-hidden=\"true\" class=\"close\">&times;</button>
                        #{msg}
                    </div>"

                    el.css
                        position: 'absolute'
                        width: '100%'
                        zIndex: 1500

                    time = setTimeout ->
                        el.remove()
                    , 3000

                    el.appendTo _msgEl

                    return

                Msg.alert = (msg) ->
                    Msg.pushMsg(msg)

                Msg.success = (msg) ->
                    Msg.pushMsg(msg, 'success')

                Msg.error = (msg) ->
                    Msg.pushMsg(msg, 'danger')

                this.$get = -> Msg

                return Msg

           )

