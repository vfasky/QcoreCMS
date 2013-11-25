define ['angular', 'admin/services', 'jQuery', 'bootstrap'], (angular, services, $) ->
    'use strict'

    angular.module('admin.directives', ['admin.services'])
           .directive('appVersion', ['version', (version) ->
                (scope, element, attr) ->
                    element.text(version)
            ])
            .directive('toolTip', [ ->
                (scope, element, attr) ->
                    tip       = attr.toolTip
                    placement = attr.placement ? 'top'
                    trigger   = attr.trigger ? 'hover'
                    el        = $(element)

                    el.tooltip
                        placement: placement
                        trigger: trigger
                        title: tip

            ])
            .directive('wtforms', ['$compile', '$timeout', ($compile, $timeout) ->
                (scope, element, attr) ->
                    modelName = attr.wtforms ? 'form'
                    el        = $(element)
                    submitAct = attr.submitAct ? ''
                    tpl       = "
                        <form method=\"post\" name=\"#{modelName}\" ng-submit=\"#{submitAct}\" class=\"form-horizontal\" role=\"form\">
                            <div ng-repeat=\"field in #{modelName}\">
                                    <div ng-if=\"field.type == 'HiddenField'\">
                                        <input type=\"hidden\" name=\"{{field.name}}\" ng-model=\"field.data\">
                                    </div>

                                    <div class=\"form-group\" ng-if=\"field.type == 'TextField'\">
                                        <label for=\"wt-#{modelName}-{{ field.name }}\" class=\"col-sm-2 control-label\">{{ field.label }}:</label>
                                        <div class=\"col-sm-10\" ng-if=\"!field.disabled\">
                                            <input id=\"wt-#{modelName}-{{ field.name }}\" ng-if=\"field.required\" class=\"form-control\" type=\"text\" name=\"{{field.name}}\" ng-model=\"field.data\" required>
                                            <input id=\"wt-#{modelName}-{{ field.name }}\" ng-if=\"!field.required\" class=\"form-control\" type=\"text\" name=\"{{field.name}}\" ng-model=\"field.data\">
                                            <p class=\"help-block\">{{ field.description }}</p>
                                        </div>
                                        <div class=\"col-sm-10\" ng-if=\"field.disabled\">
                                            <input id=\"wt-#{modelName}-{{ field.name }}\" class=\"form-control\" type=\"text\" name=\"{{field.name}}\" ng-model=\"field.data\" disabled>
                                            <p class=\"help-block\">{{ field.description }}</p>
                                        </div>
                                    </div>

                                    <div class=\"form-group\" ng-if=\"field.type == 'TextAreaField'\">
                                        <label for=\"wt-#{modelName}-{{ field.name }}\" class=\"col-sm-2 control-label\">{{ field.label }}:</label>
                                        <div class=\"col-sm-10\" ng-if=\"!field.disabled\">
                                            <textarea rows=\"3\" id=\"wt-#{modelName}-{{ field.name }}\" ng-if=\"field.required\" class=\"form-control\" type=\"text\" name=\"{{field.name}}\" ng-model=\"field.data\" required></textarea>
                                            <textarea rows=\"3\" id=\"wt-#{modelName}-{{ field.name }}\" ng-if=\"!field.required\" class=\"form-control\" type=\"text\" name=\"{{field.name}}\" ng-model=\"field.data\"></textarea>
                                            <p class=\"help-block\">{{ field.description }}</p>
                                        </div>
                                        <div class=\"col-sm-10\" ng-if=\"field.disabled\">
                                            <textarea rows=\"3\" id=\"wt-#{modelName}-{{ field.name }}\" class=\"form-control\" type=\"text\" name=\"{{field.name}}\" ng-model=\"field.data\" disabled></textarea>
                                            <p class=\"help-block\">{{ field.description }}</p>
                                        </div>
                                    </div>

                                    <div class=\"form-group\" ng-if=\"field.type == 'SelectField'\">
                                        <label for=\"wt-#{modelName}-{{ field.name }}\" class=\"col-sm-2 control-label\">{{ field.label }}:</label>
                                        <div class=\"col-sm-10\" ng-if=\"!field.disabled\">
                                            <select id=\"wt-#{modelName}-{{ field.name }}\" class=\"form-control\" name=\"{{field.name}}\" ng-model=\"field.data\" required>
                                                <option ng-selected=\"field.data == v.value\" ng-repeat=\"v in field.choices\" value=\"{{v.value}}\">
                                                    {{v.label}}
                                                </option>
                                            </select>
                                            <p class=\"help-block\">{{ field.description }}</p>

                                        </div>
                                        <div class=\"col-sm-10\" ng-if=\"field.disabled\">
                                            <select id=\"wt-#{modelName}-{{ field.name }}\" class=\"form-control\" name=\"{{field.name}}\" ng-model=\"field.data\" disabled>
                                                <option ng-selected=\"field.data == v.value\" ng-repeat=\"v in field.choices\" value=\"{{v.value}}\">
                                                    {{v.label}}
                                                </option>
                                            </select>
                                            <p class=\"help-block\">{{ field.description }}</p>

                                        </div>
                                    </div>
                                    
                            </div>
                            <div class=\"form-group\">
                                <div class=\"col-sm-offset-2 col-sm-10\">
                                    <button type=\"submit\" class=\"btn btn-primary\">
                                        保存
                                    </button>
                                </div>
                            </div>
                        </form>
                    "
                    formEl = $ tpl

                    formEl.appendTo el
                    $compile(formEl[0])(scope)
               
            ])




    return
