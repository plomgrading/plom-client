import traceback
from plom.plom_exceptions import PlomConnectionError, PlomAuthenticationException, PlomExistingLoginException

from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.views import View
from django.views.generic.base import TemplateView
from braces.views import GroupRequiredMixin, LoginRequiredMixin

from TestCreator.services import TestSpecService, TestSpecGenerateService
from Preparation.services import PQVMappingService

from Connect.services import CoreConnectionService
from Connect.forms import CoreConnectionForm, CoreManagerLoginForm


class ManagerRequiredUtilView(GroupRequiredMixin, LoginRequiredMixin, View):
    login_url = "login"
    group_required = [u"manager"]

    def build_context(self):
        """Get context dict with navbar colour and user group"""
        context = {
            "navbar_colour": "#AD9CFF",
            "user_group": "manager",
        }
        return context


class ManagerRequiredTemplateView(GroupRequiredMixin, LoginRequiredMixin, TemplateView):
    login_url = "login"
    group_required = [u"manager"]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["navbar_colour"] = "#AD9CFF"
        context["user_group"] = "manager"
        return context


class ConnectServerManagerView(ManagerRequiredTemplateView):
    template_name = 'Connect/connect-manager-page.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        core = CoreConnectionService()

        url = core.get_server_name()
        port = core.get_port_number()
        context['form'] = CoreConnectionForm(initial={
            'server_url': url if url else 'localhost', 
            'port_number': port if port else 41984
            })

        manager = core.get_manager()
        context['manager_form'] = CoreManagerLoginForm(initial={
            'password': manager.password
        })

        context['is_valid'] = core.is_there_a_valid_connection()
        context['manager_logged_in'] = core.is_manager_authenticated()
        return context


class ConnectSendInfoToCoreView(ManagerRequiredTemplateView):
    template_name = 'Connect/connect-send-info-page.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        spec = TestSpecService()
        core = CoreConnectionService()
        qvs = PQVMappingService()

        context['is_valid'] = core.is_there_a_valid_connection()
        context['manager_details_available'] = core.is_manager_authenticated()
        context['spec_valid'] = spec.is_specification_valid()
        context['is_spec_sent'] = core.has_test_spec_been_sent()
        context['pqvmap_exists'] = qvs.is_there_a_pqv_map()

        return context


class AttemptCoreConnectionView(ManagerRequiredUtilView):
    """Ping the core server with the URL, api version, and client version"""

    def post(self, request):
        """If the connection is valid, save core server details"""
        form_data = request.POST
        url = form_data['server_url']
        port_number = form_data['port_number']

        core = CoreConnectionService()

        try:
            version_string = core.validate_url(url, port_number)

            if version_string:
                core.save_connection_info(url, port_number, version_string)
                return HttpResponse(f'<p id="result" class="text-success">Connection successful! {version_string}</p>')

        except PlomConnectionError as e:
            print(e)
            return HttpResponse(f'<p id="result" style="color: red;">Unable to connect to Plom Classic. Is the server running?</p>')
        except Exception as e:
            exception_string = traceback.format_exc(chain=False)
            print(exception_string)
            print(type(exception_string))
            return HttpResponse(f'<p id="result" style="color: red;">{exception_string}</p>') 


class ForgetCoreConnectionView(ManagerRequiredUtilView):
    """Remove the current core server info from the database"""
    def post(self, request):
        core = CoreConnectionService()
        core.forget_connection_info()
        return HttpResponse('<p id="result">Connection details cleared.</p>')
        

class AttemptCoreManagerLoginView(ManagerRequiredUtilView):
    """Log in as the core server manager account"""

    def post(self, request):
        form_data = request.POST
        password = form_data['password']

        core = CoreConnectionService()

        try:
            manager = core.authenticate_manager(password)
            return HttpResponse(f'<p id="manager_result" class="text-success">Manager login successful!</p>')
        except Exception as e:
            print(e)
            return HttpResponse(f'<p id="manager_result" style="color: red;">{e}</p>')


class ForgetCoreManagerLoginView(ManagerRequiredUtilView):
    """Remove the manager login details from the database"""

    def post(self, request):
        core = CoreConnectionService()
        core.forget_manager()
        return HttpResponse('<p id="manager_result">Manager details cleared.</p>')


class SendTestSpecToCoreView(ManagerRequiredUtilView):
    def post(self, request):
        """Send test specification data to the core server"""
        core = CoreConnectionService()
        spec = TestSpecService()
        spec_dict = TestSpecGenerateService(spec).generate_spec_dict()

        try:
            core.send_test_spec(spec_dict)
            context = self.build_context()
            context.update({'attempt': True})
            return render(request, 'Connect/connect-test-spec-attempt.html', context)
        except PlomConnectionError as e:
            print(e)
            context = self.build_context()
            context.update({
                'attempt': False,
                'exception': "Unable to connect to Plom-classic. Is the server running?",
            })
            return render(request, 'Connect/connect-test-spec-attempt.html', context)
        except Exception as e:
            print(e)
            context = self.build_context()
            context.update({
                'attempt': False,
                'exception': e
            })
            return render(request, 'Connect/connect-test-spec-attempt.html', context)


class SendPQVInitializeDB(ManagerRequiredUtilView):
    def post(self, request):
        """Send PQV map to core and initialize the database"""
        core = CoreConnectionService()
        qvs = PQVMappingService()

        try:
            ver_map = qvs.get_pqv_map_dict()
            core.initialize_core_db(ver_map)
            context = self.build_context()
            context.update({'attempt': True})
            return render(request, 'Connect/connect-vermap-attempt.html', context)
        except PlomConnectionError as e:
            print(e)
            context = self.build_context()
            context.update({
                'attempt': False,
                'exception': "Unable to connect to Plom-classic. Is the server running?",
            })
            return render(request, 'Connect/connect-vermap-attempt.html', context)
        except Exception as e:
            print(e)
            context = self.build_context()
            context.update({
                'attempt': False,
                'exception': e
            })
            return render(request, 'Connect/connect-vermap-attempt.html', context)

