define ['jQuery', 'admin/app', 'bootstrap'], ($, app)->
    _msgEl = $ "<div></div>" 

    _msgEl.css 
        position: 'absolute'
        width: 200
        top: 2
        left: '50%'
        marginLeft: -200
        zIndex: 1500

    app.provider 'Msg', ->
        Msg = {}
        Msg.pushMsg = (msg, type='warning') ->
            el = $ "
            <div class=\"alert alert-#{type}\">
                <button type=\"button\" class=\"close\">&times;</button>
                #{msg}
            </div>"

            time = setTimeout ->
                el.remove()
            , 3000

            el.on('click', 'button.close', ->
                if time
                    clearTimeout time

                el.remove()
                false
            )

            el.appendTo _msgEl

            return

        Msg.alert = (msg) ->
            Msg.pushMsg(msg)

        Msg.success = (msg) ->
            Msg.pushMsg(msg, 'success')

        Msg.error = (msg) ->
            Msg.pushMsg(msg, 'danger')

        this.$get = -> Msg

    $ -> _msgEl.appendTo 'body'

    app