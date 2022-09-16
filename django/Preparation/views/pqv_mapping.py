from django.shortcuts import render

from django.http import HttpResponseRedirect, HttpResponse
from django_htmx.http import HttpResponseClientRedirect

from Preparation.services import (
    PQVMappingService,
    PrenameSettingService,
    StagingStudentService,
)

from Base.base_group_views import ManagerRequiredView
from SpecCreator.services import StagingSpecificationService
from Papers.services import SpecificationService

class PQVMappingUploadView(ManagerRequiredView):
    # NOT CURRENTLY BEING USED
    def post(self, request):
        context = {}
        return render(request, "Preparation/pqv_mapping_attempt.html", context)


class PQVMappingDownloadView(ManagerRequiredView):
    def get(self, request):
        pqvs = PQVMappingService()
        pqvs_csv_txt = pqvs.get_pqv_map_as_csv()
        return HttpResponse(pqvs_csv_txt, content_type="text/plain")


class PQVMappingDeleteView(ManagerRequiredView):
    def delete(self, request):
        pqvs = PQVMappingService()
        pqvs.remove_pqv_map()
        return HttpResponseClientRedirect(".")


class PQVMappingView(ManagerRequiredView):
    def build_context(self):
        pqvs = PQVMappingService()
        pss = PrenameSettingService()
        sss = StagingStudentService()
        speck = SpecificationService()

        context = {
            "number_of_questions": speck.get_n_questions(),
            "question_list": range(1, 1 + speck.get_n_questions()),
            "prenaming": pss.get_prenaming_setting(),
            "pqv_mapping_present": pqvs.is_there_a_pqv_map(),
            "number_of_students": sss.how_many_students(),
            "student_list_present": sss.are_there_students(),
            "navbar_colour": "#AD9CFF",
            "user_group": "manager",
        }
        fpp, lpp = sss.get_first_last_prenamed_paper()
        context.update({"first_prenamed_paper": fpp, "last_prenamed_paper": lpp})

        context["min_number_to_produce"] = sss.get_minimum_number_to_produce()

        if context["pqv_mapping_present"]:
            context["pqv_table"] = pqvs.get_pqv_map_as_table(
                prenaming=context["prenaming"]
            )
            context["pqv_number_rows"] = len(context["pqv_table"])
            
        return context

    def get(self, request):
        context = self.build_context()
        return render(request, "Preparation/pqv_mapping_manage.html", context)

    def post(self, request):
        ntp = request.POST.get("number_to_produce", None)
        if not ntp:
            return HttpResponseRedirect(".")
        try:
            number_to_produce = int(ntp)
        except ValueError:
            return HttpResponseRedirect(".")

        pqvs = PQVMappingService()
        staged_spec = StagingSpecificationService()
        pqvs.generate_and_set_pqvmap(number_to_produce)
        staged_spec.set_n_to_produce(number_to_produce)
        spec_dict = staged_spec.get_valid_spec_dict()
        
        speck = SpecificationService()
        speck.store_validated_spec(spec_dict)
        return HttpResponseRedirect(".")
