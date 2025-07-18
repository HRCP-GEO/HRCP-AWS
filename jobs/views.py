import random
import string

from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.db.models import Q
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.cache import never_cache
import json
from .models import Job, Company, JobCategory, JobTimeType, Location, CVApplication
from collections import Counter
from django.shortcuts import render, redirect
from .forms import JobAdForm, CVApplicationForm
from django.conf import settings
from django.core.mail import EmailMessage
import logging
import datetime
from django.conf import settings
from django.templatetags.static import static
logger = logging.getLogger(__name__)


def job_list(request):
    JOB_TYPE_SLUG_MAP = {
        'ვაკანსია': 'vakansia',
        'ტრენინგი/განათლება': 'treningi/ganatleba',
        'ტენდერი': 'tenderi',
        'სხვა': 'sxva'
    }
    REVERSE_JOB_TYPE_SLUG_MAP = {v: k for k, v in JOB_TYPE_SLUG_MAP.items()}

    SALARY_FILTER_OPTIONS = {
        'all': 'ყველა (ხელფასი)',  # Clarify it means all regarding salary
        '500': '500+',
        '1000': '1000+',
        '1500': '1500+',
        '2000': '2000+',
        '2500': '2500+',
        '5000': '5000+',
    }
    SALARY_MINIMUMS = {  # Map option keys to numeric minimums
        '500': 500,
        '1000': 1000,
        '1500': 1500,
        '2000': 2000,
        '2500': 2500,
        '5000': 5000,
    }

    min_salary_key = request.GET.get('min_salary', 'all')  # Default to 'all'

    # --- Query Params ---
    query = request.GET.get('q', '')
    location_slug = request.GET.get('location', '')
    category_slug = request.GET.get('category', '')
    job_type_slug = request.GET.get('job_type', '')
    job_type = REVERSE_JOB_TYPE_SLUG_MAP.get(job_type_slug, '')
    has_salary = request.GET.get('has_salary', '')
    is_foreign_language = request.GET.get('is_foreign_language', '')
    job_time_type_slugs = request.GET.getlist('job_time_types')
    page = int(request.GET.get('page', 1))
    per_page = 10

    # --- Slug-based object lookups (for Georgian name display) ---
    selected_location_obj = None
    selected_category_obj = None

    if location_slug and location_slug != 'all':
        try:
            selected_location_obj = Location.objects.get(slug=location_slug)
        except Location.DoesNotExist:
            selected_location_obj = None

    if category_slug and category_slug != 'all':
        try:
            selected_category_obj = JobCategory.objects.get(slug=category_slug)
        except JobCategory.DoesNotExist:
            selected_category_obj = None

    # --- Base queryset ---
    jobs = Job.objects.prefetch_related(
        'locations', 'job_time_types', 'company', 'category'
    ).all().order_by('-created_at')

    # --- Filters ---
    if query:
        jobs = jobs.filter(Q(title__icontains=query) | Q(company__name__icontains=query))

    if selected_location_obj:
        jobs = jobs.filter(locations=selected_location_obj)

    if job_type and job_type != 'all':
        jobs = jobs.filter(job_type=job_type)

    if selected_category_obj:
        jobs = jobs.filter(category=selected_category_obj)

    if has_salary == 'true':
        jobs = jobs.filter(has_salary=True)

    if is_foreign_language == 'true':
        jobs = jobs.filter(is_foreign_language=True)

    if job_time_type_slugs and 'all' not in job_time_type_slugs:
        jobs = jobs.filter(job_time_types__slug__in=job_time_type_slugs).distinct()

    if min_salary_key != 'all' and min_salary_key in SALARY_MINIMUMS:
        min_amount = SALARY_MINIMUMS[min_salary_key]
        jobs = jobs.filter(has_salary=True, salary_amount__gte=min_amount)

    # --- Pagination ---
    start_index = (page - 1) * per_page
    end_index = page * per_page

    vip_jobs = jobs.filter(is_vip=True)
    regular_jobs = jobs.filter(is_vip=False)

    total_regular_jobs = regular_jobs.count()
    regular_jobs_page = regular_jobs[start_index:end_index]

    # --- Mark "last day" jobs ---
    today = timezone.now().date()
    for job_list_chunk in [vip_jobs, regular_jobs_page]:
        for job in job_list_chunk:
            job.is_last_day = job.expired_jobs.date() == today

    # --- AJAX response for infinite scroll ---
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        html = render_to_string('jobs/job_cards_partial.html', {
            'regular_jobs': regular_jobs_page,
        }, request=request)

        return JsonResponse({
            'html': html,
            'has_more': end_index < total_regular_jobs,
            'total': total_regular_jobs,
        })
    selected_min_salary_label = SALARY_FILTER_OPTIONS.get(min_salary_key,
                                                          'ხელფასი (+/-)')  # Default text if key not found or is 'all' (though 'all' has its own entry)
    # --- All filter options for UI ---
    all_locations = Location.objects.all()
    all_categories = JobCategory.objects.all()
    all_job_time_types = JobTimeType.objects.all().order_by('id')
    job_types = [jt[0] for jt in Job.JOB_TYPES]

    any_job_has_salary = Job.objects.filter(has_salary=True).exists()
    base_query_params = request.GET.copy()

    any_job_is_foreign_language = Job.objects.filter(is_foreign_language=True).exists()

    # --- Render main page ---
    return render(request, "jobs/home.html", {
        "query": query,
        "selected_location": location_slug,
        "selected_location_obj": selected_location_obj,
        "category": category_slug,
        "selected_category_obj": selected_category_obj,
        # "job_type": job_type,
        "has_salary": has_salary,
        "locations": all_locations,
        "categories": all_categories,
        "job_types": job_types,
        "job_time_types": all_job_time_types,
        "selected_job_time_types": job_time_type_slugs,
        "salary_options": SALARY_FILTER_OPTIONS,
        "selected_min_salary": min_salary_key,  # Pass the selected key
        "vip_jobs": vip_jobs,
        "regular_jobs": regular_jobs_page,
        "total_regular_jobs": total_regular_jobs,
        "has_more": end_index < total_regular_jobs,
        "current_page": page,
        "any_job_has_salary": any_job_has_salary,
        "companies": Company.objects.filter(is_vip=True),
        "base_query_params": base_query_params.urlencode(),
        "job_type": job_type_slug,
        "selected_job_type_label": job_type or None,  # For Georgian UI
        "job_type_slug_map": JOB_TYPE_SLUG_MAP,
        "selected_min_salary_label": selected_min_salary_label,
        "any_job_is_foreign_language": any_job_is_foreign_language,
        "is_foreign_language": is_foreign_language,
    })


def jobs_by_company(request, company_slug):
    company = get_object_or_404(Company, slug=company_slug)
    # Start with jobs for this company ONLY
    jobs_queryset = Job.objects.filter(company=company).prefetch_related(
        'locations', 'job_time_types', 'category'  # Prefetch for efficiency in the template
    ).all().order_by('-created_at')

    # Get the search query parameter (use 'q' for consistency)
    query = request.GET.get('q', '')

    # Apply search filter IF a query exists
    if query:
        # Filter by job title containing the query within this company's jobs
        jobs_queryset = jobs_queryset.filter(title__icontains=query)

    # The job_time_type filter is removed as the UI element was removed

    return render(request, "jobs/jobs_by_company.html", {
        "jobs": jobs_queryset,  # Pass the filtered queryset
        "company": company,
        "query": query,  # Pass the current query back to the template
        # Removed 'search_term' and 'job_time_type' context variables
    })


def job_detail(request, id, job_slug):
    job = get_object_or_404(Job, id=id, slug=job_slug)
    companies = Company.objects.all()

    is_last_day = False
    if job.expired_jobs.date() == timezone.now().date():
        is_last_day = True

    # Initialize CV form
    cv_form = CVApplicationForm()

    return render(request, 'jobs/job_detail.html', {
        'job': job, 
        'companies': companies, 
        'is_last_day': is_last_day,
        'cv_form': cv_form
    })


def partners_showcase(request):
    companies = Company.objects.all()
    return render(request, "jobs/company_boxes.html", {"companies": companies})


PRODUCT_PRICES = {
    "standard": 30,
    "standard_logo": 50,
    "vip_ad": 100,
    "vip_logo": 120,
    "training": 30,
    "training_logo": 50,
    "tender": 30,
    "tender_logo": 50
}


@never_cache
def post_job_ad(request):
    if request.method == "POST":
        form = JobAdForm(request.POST, request.FILES)
        if form.is_valid():
            selected_products = form.cleaned_data.get("products", [])
            total_price = sum(PRODUCT_PRICES.get(p, 0) for p in selected_products if p in PRODUCT_PRICES)

            # Server-side validation for product keys
            if any(p not in PRODUCT_PRICES for p in selected_products):
                logger.warning(f"Invalid product key detected in submission: {selected_products}")
                product_prices_json = json.dumps(PRODUCT_PRICES)
                form.PRODUCT_CHOICES_DICT = dict(JobAdForm.PRODUCT_CHOICES)
                return render(request, "jobs/post_job.html", {
                    "form": form,
                    "product_prices_json": product_prices_json,
                    "error": "An invalid product was detected. Please try again.",
                })

            def generate_random_string(length=4):
                characters = string.ascii_letters + string.digits
                return ''.join(random.choice(characters) for _ in range(length))

            # Prepare email content
            now = datetime.datetime.now()
            random_suffix = generate_random_string()
            subject = f"გამოქვეყნების განცხადება - HRCP.GE - {now} - {random_suffix}"
            form.PRODUCT_CHOICES_DICT = dict(JobAdForm.PRODUCT_CHOICES)
            product_counts = Counter(selected_products)
            product_summary = "\n".join([f"  - {form.PRODUCT_CHOICES_DICT.get(p, p)}: {count} ერთეული"
                                         for p, count in product_counts.items()])

            message = f"""
            ახალი განცხადება გამოქვეყნებისთვის საიტზე HRCP.GE:

            **ინფორმაცია კომპანიის შესახებ**
            საიდენტიფიკაციო კოდი: {form.cleaned_data.get("identification_code")}
            კომპანიის დასახელება: {form.cleaned_data.get("company_name")}
            ელფოსტა: {form.cleaned_data.get("company_email")}
            ტელეფონი: {form.cleaned_data.get("phone")}
            დამატებითი მეილი: {form.cleaned_data.get("additional_email") or '-'}

            **განცხადების დეტალები**
            განცხადების ტიპი: {form.cleaned_data.get("advertisement_type")}
            განცხადების დასახელება: {form.cleaned_data.get("advertisement_name")}
            ვაკანსიის აღწერა:
            --------------------
            {form.cleaned_data.get("vacancy_description")}
            --------------------
            დამატებითი კომენტარი: {form.cleaned_data.get("comment") or '-'}

            **არჩეული პროდუქტები**
            {product_summary}

            **საბოლოო ფასი (სერვერზე დათვლილი): {total_price} GEL**
            """

            # recipient_email = settings.DEFAULT_ADMIN_EMAIL
            # recipient_email = "raforafo26@gmail.com" # Keep yours if intended
            recipient_email =  settings.ADMIN_EMAIL
            # Create EmailMessage object ONCE
            email = EmailMessage(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [recipient_email]
                # Optional: headers={'Reply-To': form.cleaned_data.get("company_email")}
            )

            # Attach files ONCE before sending
            for field in ['document', 'company_logo']:
                file = form.cleaned_data.get(field)
                if file:
                    try:
                        # It's safer to read the file content again if attaching
                        # File objects might have their read pointers at the end after validation/saving
                        file.seek(0)  # Reset read pointer
                        email.attach(file.name, file.read(), file.content_type)
                    except Exception as attach_error:
                        logger.error(f"Error attaching file {field} ({getattr(file, 'name', 'N/A')}): {attach_error}")
                        # Decide if you want to continue sending without the file or show an error

            # Send the email ONCE
            try:
                email.send(fail_silently=False)
                logger.info(f"Job ad submission email sent successfully for {form.cleaned_data.get('company_name')}")
                # Redirect ONLY after successful send
                return redirect(reverse('success_page'))

            except Exception as e:
                logger.error(f"Error sending job ad submission email: {e}")
                # Prepare context for error display
                product_prices_json = json.dumps(PRODUCT_PRICES)
                form.PRODUCT_CHOICES_DICT = dict(JobAdForm.PRODUCT_CHOICES)
                return render(request, "jobs/post_job.html", {
                    "form": form,
                    "product_prices_json": product_prices_json,
                    "error": "An error occurred while sending your request. Please contact support or try again later.",
                })

            # DO NOT redirect here if email sending failed above

        else:  # Form is invalid
            logger.warning(f"Job Ad Form validation failed: {form.errors.as_json()}")
            product_prices_json = json.dumps(PRODUCT_PRICES)
            form.PRODUCT_CHOICES_DICT = dict(JobAdForm.PRODUCT_CHOICES)
            context = {
                "form": form,
                "product_prices_json": product_prices_json,
            }
            response = render(request, "jobs/post_job.html", context)
            response["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
            response["Pragma"] = "no-cache"
            response["Expires"] = "0"
            return response

    else:  # GET Request
        form = JobAdForm()
        product_prices_json = json.dumps(PRODUCT_PRICES)
        form.PRODUCT_CHOICES_DICT = dict(JobAdForm.PRODUCT_CHOICES)
        context = {
            "form": form,
            "product_prices_json": product_prices_json,
        }
        response = render(request, "jobs/post_job.html", context)
        response["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
        response["Pragma"] = "no-cache"
        response["Expires"] = "0"
        return response


def success_page(request):
    # Once the user is on the success page, we can show a confirmation message.
    return render(request, 'jobs/success.html')


def contact_page(request):
    return render(request, 'jobs/contact_page.html')


def faq_page(request):
    return render(request, 'jobs/faq_page.html')


def banner_page(request):
    return render(request, 'jobs/banner_page.html')


def custom_404(request, exception):
    return render(request, 'jobs/404.html', status=404)


def submit_cv(request, job_id):
    if request.method == 'POST':
        job = get_object_or_404(Job, id=job_id)
        form = CVApplicationForm(request.POST, request.FILES)
        
        if form.is_valid():
            try:
                now = timezone.now()
                now_str = now.strftime("%Y-%m-%d %H:%M:%S")
                random_suffix = ''.join(random.choices(string.digits, k=4))
                subject = f"CV მიღებულია: {job.title} - {now_str} (ID: {random_suffix})"
                
                first_name = form.cleaned_data['first_name']
                last_name = form.cleaned_data['last_name']
                email_address = form.cleaned_data['email']
                mobile_number = form.cleaned_data['mobile_number']
                cv_file = form.cleaned_data['cv_file']

                # Build absolute URL for job detail
                if request.is_secure():
                    scheme = 'https://'
                else:
                    scheme = 'http://'
                domain = request.get_host()
                job_url = scheme + domain + job.get_absolute_url()
                logo_url = scheme + domain + static('HRCP_200.png')

                # 1. Email to job poster company (HTML)
                company_email = job.company.email
                if not company_email:
                    return JsonResponse({'success': False, 'message': 'კომპანიის ელფოსტა ვერ მოიძებნა.'})
                
                message_to_company = f"""
                <div style='font-family:Arial,sans-serif;max-width:500px;margin:auto;border:1px solid #eee;padding:24px;'>
                  <div style='text-align:center;margin-bottom:24px;'>
                    <img src='{logo_url}' alt='HRCP Logo' style='max-width:120px;'>
                  </div>
                  <h2 style='color:#36B37E;margin-bottom:8px;'>ახალი CV განაცხადი</h2>
                  <p style='margin:0 0 16px 0;'>ვაკანსია: <a href='{job_url}' style='color:#0052cc;text-decoration:none;font-weight:600;'>{job.title}</a></p>
                  <p style='margin:0 0 16px 0;'>კომპანია: <b>{job.company.name}</b></p>
                  <hr style='margin:24px 0;'>
                  <h3 style='color:#172B4D;margin-bottom:8px;'>მომხმარებლის ინფორმაცია</h3>
                  <ul style='padding-left:18px;margin:0 0 16px 0;'>
                    <li>სახელი: <b>{first_name}</b></li>
                    <li>გვარი: <b>{last_name}</b></li>
                    <li>ელ-ფოსტა: <b>{email_address}</b></li>
                    <li>მობილური ნომერი: <b>{mobile_number}</b></li>
                    <li>განაცხადის თარიღი: <b>{now_str}</b></li>
                  </ul>
                  <p style='margin:0 0 16px 0;'>CV ფაილი მიმაგრებულია ამავე მეილზე.</p>
                  <div style='margin-top:32px;font-size:13px;color:#888;'>ეს ვაკანსია და განაცხადი გამოგზავნილია ვებ-გვერდიდან <a href='{scheme + domain}' style='color:#36B37E;text-decoration:none;'>HRCP.GE</a></div>
                </div>
                """
                from django.core.mail import get_connection
                custom_connection = get_connection(
                    host=settings.CUSTOM_EMAIL_HOST,
                    port=settings.CUSTOM_EMAIL_PORT,
                    username=settings.CUSTOM_EMAIL_HOST_USER,
                    password=settings.CUSTOM_EMAIL_HOST_PASSWORD,
                    use_tls=settings.CUSTOM_EMAIL_USE_TLS,
                    fail_silently=False
                )

                email_msg_company = EmailMessage(
                    subject,
                    message_to_company,
                    settings.CUSTOM_EMAIL_HOST_USER,  # from_email
                    [company_email],
                    connection=custom_connection
                )
                email_msg_company.content_subtype = "html"
                if cv_file:
                    try:
                        cv_file.seek(0)
                        file_content = cv_file.read()
                        email_msg_company.attach(
                            cv_file.name, 
                            file_content, 
                            cv_file.content_type or 'application/octet-stream'
                        )
                        cv_file.seek(0)
                    except Exception as attach_error:
                        logger.error(f"Error attaching CV file: {attach_error}")
                        return JsonResponse({
                            'success': False,
                            'message': 'CV ფაილის მიმაგრებისას მოხდა შეცდომა. გთხოვთ სცადოთ თავიდან.'
                        })
                email_msg_company.send(fail_silently=False)
                
                # 2. Confirmation email to applicant (HTML)
                subject_user = f"თქვენი CV გაიგზავნა - {job.title} - {now_str} (ID: {random_suffix})"
                message_to_user = f"""
                <div style='font-family:Arial,sans-serif;max-width:500px;margin:auto;border:1px solid #eee;padding:24px;'>
                  <div style='text-align:center;margin-bottom:24px;'>
                    <img src='{logo_url}' alt='HRCP Logo' style='max-width:120px;'>
                  </div>
                  <h2 style='color:#36B37E;margin-bottom:8px;'>თქვენი CV გაიგზავნა</h2>
                  <p style='margin:0 0 16px 0;'>ვაკანსია: <a href='{job_url}' style='color:#0052cc;text-decoration:none;font-weight:600;'>{job.title}</a></p>
                  <p style='margin:0 0 16px 0;'>კომპანია: <b>{job.company.name}</b></p>
                  <hr style='margin:24px 0;'>
                  <p style='margin:0 0 16px 0;'>თქვენი CV წარმატებით გაიგზავნა შემდეგ ვაკანსიაზე.</p>
                  <p style='margin:0 0 16px 0;'>გაგზავნის თარიღი: <b>{now_str}</b></p>
                  <div style='margin-top:32px;font-size:13px;color:#888;'>მადლობა, რომ იყენებთ <a href='{scheme + domain}' style='color:#36B37E;text-decoration:none;'>HRCP.GE</a>!</div>
                </div>
                """
                email_msg_user = EmailMessage(
                    subject_user,
                    message_to_user,
                    settings.CUSTOM_EMAIL_HOST_USER,  # from_email (custom sender)
                    [email_address],
                    connection=custom_connection  # same connection as above
                )
                email_msg_user.content_subtype = "html"
                email_msg_user.send(fail_silently=False)
                
                # Save to database after successful emails
                cv_application = form.save(commit=False)
                cv_application.job = job
                cv_application.save()
                
                return JsonResponse({
                    'success': True,
                    'message': 'თქვენი CV წარმატებით გაიგზავნა!'
                })
                
            except Exception as e:
                logger.error(f"Error sending CV application email: {e}")
                return JsonResponse({
                    'success': False,
                    'message': 'CV-ის გაგზავნისას მოხდა შეცდომა. გთხოვთ სცადოთ თავიდან.'
                })
        else:
            errors = form.errors.as_json()
            logger.warning(f"CV Form validation failed: {errors}")
            return JsonResponse({
                'success': False,
                'message': 'გთხოვთ შეავსოთ ყველა სავალდებულო ველი სწორად.',
                'errors': errors
            })
    
    return JsonResponse({'success': False, 'message': 'არასწორი მოთხოვნა.'})
