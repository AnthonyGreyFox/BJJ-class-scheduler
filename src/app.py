from flask import Flask, render_template, request, redirect, url_for, session, send_file, flash, abort
from flask_session import Session
import os
import json
from src.models.scheduler import BJJScheduler

import io
from datetime import date

# Helper to get or create scheduler from session

def get_scheduler():
    if 'scheduler_data' in session:
        scheduler = BJJScheduler()
        scheduler.from_dict(session['scheduler_data'])
        return scheduler
    else:
        scheduler = BJJScheduler()
        session['scheduler_data'] = scheduler.to_dict()
        return scheduler

def save_scheduler(scheduler):
    session['scheduler_data'] = scheduler.to_dict()

app = Flask(__name__)
app.secret_key = os.environ.get('BJJ_SECRET_KEY', 'dev-secret-key')
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)

# Remove or comment out the old index route
# @app.route('/')
# def index():
#     return render_template('index.html')

@app.route('/settings', methods=['GET', 'POST'])
def settings():
    scheduler = get_scheduler()
    if request.method == 'POST':
        # Update settings from form (to be implemented)
        pass
    return render_template('settings.html', scheduler=scheduler)

@app.route('/settings/download')
def download_settings():
    scheduler = get_scheduler()
    data = scheduler.to_dict()
    # Add manual assignments from session
    data['manual_assignments'] = session.get('manual_assignments', [])
    json_bytes = json.dumps(data, indent=2).encode('utf-8')
    return send_file(
        io.BytesIO(json_bytes),
        mimetype='application/json',
        as_attachment=True,
        download_name='bjj_scheduler_settings.json'
    )

@app.route('/settings/upload', methods=['POST'])
def upload_settings():
    if 'settings_file' not in request.files:
        flash('No file part')
        return redirect(url_for('settings'))
    file = request.files['settings_file']
    if file.filename == '':
        flash('No selected file')
        return redirect(url_for('settings'))
    try:
        data = json.load(file)
        scheduler = BJJScheduler()
        scheduler.from_dict(data)
        save_scheduler(scheduler)
        # Restore manual assignments if present
        if 'manual_assignments' in data:
            session['manual_assignments'] = data['manual_assignments']
        else:
            session['manual_assignments'] = []
        flash('Settings uploaded successfully!')
    except Exception as e:
        flash(f'Failed to upload settings: {e}')
    return redirect(url_for('settings'))

@app.route('/coaches')
def coaches():
    scheduler = get_scheduler()
    return render_template('coaches.html', coaches=scheduler.coaches)

@app.route('/coaches/add', methods=['GET', 'POST'])
def add_coach():
    scheduler = get_scheduler()
    if request.method == 'POST':
        name = request.form['name'].strip()
        max_weekly_classes = int(request.form['max_weekly_classes'])
        preferred_times = request.form.getlist('preferred_times')
        available_days = request.form.getlist('available_days')
        can_teach_gi = 'can_teach_gi' in request.form
        can_teach_nogi = 'can_teach_nogi' in request.form
        can_teach_open_mat = 'can_teach_open_mat' in request.form
        from src.models.data_classes import Coach
        coach = Coach(
            name=name,
            max_weekly_classes=max_weekly_classes,
            preferred_times=preferred_times,
            available_days=available_days,
            can_teach_gi=can_teach_gi,
            can_teach_nogi=can_teach_nogi,
            can_teach_open_mat=can_teach_open_mat
        )
        scheduler.add_coach(coach)
        save_scheduler(scheduler)
        flash('Coach added!')
        return redirect(url_for('coaches'))
    return render_template('coach_form.html', action='Add', coach=None)

@app.route('/coaches/edit/<int:index>', methods=['GET', 'POST'])
def edit_coach(index):
    scheduler = get_scheduler()
    if index < 0 or index >= len(scheduler.coaches):
        abort(404)
    coach = scheduler.coaches[index]
    if request.method == 'POST':
        coach.name = request.form['name'].strip()
        coach.max_weekly_classes = int(request.form['max_weekly_classes'])
        coach.preferred_times = request.form.getlist('preferred_times')
        coach.available_days = request.form.getlist('available_days')
        coach.can_teach_gi = 'can_teach_gi' in request.form
        coach.can_teach_nogi = 'can_teach_nogi' in request.form
        coach.can_teach_open_mat = 'can_teach_open_mat' in request.form
        save_scheduler(scheduler)
        flash('Coach updated!')
        return redirect(url_for('coaches'))
    return render_template('coach_form.html', action='Edit', coach=coach, index=index)

@app.route('/coaches/delete/<int:index>', methods=['POST'])
def delete_coach(index):
    scheduler = get_scheduler()
    if index < 0 or index >= len(scheduler.coaches):
        abort(404)
    del scheduler.coaches[index]
    save_scheduler(scheduler)
    flash('Coach deleted!')
    return redirect(url_for('coaches'))

@app.route('/time-slots')
def time_slots():
    scheduler = get_scheduler()
    return render_template('time_slots.html', time_slots=scheduler.time_slots)

@app.route('/time-slots/add', methods=['GET', 'POST'])
def add_time_slot():
    scheduler = get_scheduler()
    class_types = ['gi', 'no-gi', 'open-mat', 'none']
    if request.method == 'POST':
        day = request.form['day']
        start_hour = int(request.form['start_hour'])
        start_minute = int(request.form['start_minute'])
        end_hour = int(request.form['end_hour'])
        end_minute = int(request.form['end_minute'])
        primary_preference = request.form.get('primary_preference')
        secondary_preference = request.form.get('secondary_preference')
        if primary_preference == 'none':
            primary_preference = None
        if secondary_preference == 'none':
            secondary_preference = None
        from datetime import time
        from src.models.data_classes import TimeSlot
        time_slot = TimeSlot(
            day=day,
            start_time=time(start_hour, start_minute),
            end_time=time(end_hour, end_minute),
            primary_preference=primary_preference,
            secondary_preference=secondary_preference
        )
        scheduler.add_time_slot(time_slot)
        save_scheduler(scheduler)
        flash('Time slot added!')
        return redirect(url_for('time_slots'))
    return render_template('time_slot_form.html', action='Add', time_slot=None, class_types=class_types)

@app.route('/time-slots/edit/<int:index>', methods=['GET', 'POST'])
def edit_time_slot(index):
    scheduler = get_scheduler()
    class_types = ['gi', 'no-gi', 'open-mat', 'none']
    if index < 0 or index >= len(scheduler.time_slots):
        abort(404)
    time_slot = scheduler.time_slots[index]
    if request.method == 'POST':
        day = request.form['day']
        start_hour = int(request.form['start_hour'])
        start_minute = int(request.form['start_minute'])
        end_hour = int(request.form['end_hour'])
        end_minute = int(request.form['end_minute'])
        primary_preference = request.form.get('primary_preference')
        secondary_preference = request.form.get('secondary_preference')
        if primary_preference == 'none':
            primary_preference = None
        if secondary_preference == 'none':
            secondary_preference = None
        from datetime import time
        from src.models.data_classes import TimeSlot
        # Create a new TimeSlot instead of modifying the existing one (since it's frozen)
        new_time_slot = TimeSlot(
            day=day,
            start_time=time(start_hour, start_minute),
            end_time=time(end_hour, end_minute),
            primary_preference=primary_preference,
            secondary_preference=secondary_preference
        )
        scheduler.time_slots[index] = new_time_slot
        save_scheduler(scheduler)
        flash('Time slot updated!')
        return redirect(url_for('time_slots'))
    return render_template('time_slot_form.html', action='Edit', time_slot=time_slot, index=index, class_types=class_types)

@app.route('/time-slots/delete/<int:index>', methods=['POST'])
def delete_time_slot(index):
    scheduler = get_scheduler()
    if index < 0 or index >= len(scheduler.time_slots):
        abort(404)
    del scheduler.time_slots[index]
    save_scheduler(scheduler)
    flash('Time slot deleted!')
    return redirect(url_for('time_slots'))

@app.route('/class-types')
def class_types():
    scheduler = get_scheduler()
    return render_template('class_types.html', class_types=scheduler.class_definitions)

@app.route('/class-types/add', methods=['GET', 'POST'])
def add_class_type():
    scheduler = get_scheduler()
    from src.models.enums import ClassType
    if request.method == 'POST':
        name = request.form['name'].strip()
        class_type = ClassType(request.form['class_type'])
        duration_minutes = int(request.form['duration_minutes'])
        weekly_count = int(request.form['weekly_count'])
        from src.models.data_classes import ClassDefinition
        class_def = ClassDefinition(
            name=name,
            class_type=class_type,
            duration_minutes=duration_minutes,
            weekly_count=weekly_count
        )
        scheduler.add_class_definition(class_def)
        save_scheduler(scheduler)
        flash('Class type added!')
        return redirect(url_for('class_types'))
    return render_template('class_type_form.html', action='Add', class_type_obj=None)

@app.route('/class-types/edit/<int:index>', methods=['GET', 'POST'])
def edit_class_type(index):
    scheduler = get_scheduler()
    from src.models.enums import ClassType
    if index < 0 or index >= len(scheduler.class_definitions):
        abort(404)
    class_type_obj = scheduler.class_definitions[index]
    if request.method == 'POST':
        # Create a new ClassDefinition instead of modifying the existing one (since it's frozen)
        from src.models.data_classes import ClassDefinition
        new_class_def = ClassDefinition(
            name=request.form['name'].strip(),
            class_type=ClassType(request.form['class_type']),
            duration_minutes=int(request.form['duration_minutes']),
            weekly_count=int(request.form['weekly_count'])
        )
        scheduler.class_definitions[index] = new_class_def
        save_scheduler(scheduler)
        flash('Class type updated!')
        return redirect(url_for('class_types'))
    return render_template('class_type_form.html', action='Edit', class_type_obj=class_type_obj, index=index)

@app.route('/class-types/delete/<int:index>', methods=['POST'])
def delete_class_type(index):
    scheduler = get_scheduler()
    if index < 0 or index >= len(scheduler.class_definitions):
        abort(404)
    del scheduler.class_definitions[index]
    save_scheduler(scheduler)
    flash('Class type deleted!')
    return redirect(url_for('class_types'))

@app.route('/', methods=['GET', 'POST'])
def unified_scheduler():
    scheduler = get_scheduler()
    # Manual assignments are stored in session
    manual_assignments = session.get('manual_assignments', [])
    # Prepare data for manual assignment form
    class_options = [cd for cd in scheduler.class_definitions if cd.weekly_count > 0]
    coach_options = scheduler.coaches
    slot_options = scheduler.time_slots
    schedule = session.get('last_schedule')
    conflicts = session.get('last_conflicts', [])
    coach_edit_idx = None
    coach_edit_data = None
    slot_edit_idx = None
    slot_edit_data = None
    class_edit_idx = None
    class_edit_data = None
    # Handle POST actions (add manual, clear manual, generate, save/upload, config modals)
    # (Stub: actual modal logic to be implemented)
    if request.method == 'POST':
        # Coach CRUD
        if 'add_coach' in request.form:
            from src.models.data_classes import Coach
            name = request.form['coach_name'].strip()
            max_weekly_classes = int(request.form['coach_max_weekly_classes'])
            preferred_times = request.form.getlist('coach_preferred_times')
            available_days = request.form.getlist('coach_available_days')
            can_teach_gi = 'coach_can_teach_gi' in request.form
            can_teach_nogi = 'coach_can_teach_nogi' in request.form
            can_teach_open_mat = 'coach_can_teach_open_mat' in request.form
            coach = Coach(
                name=name,
                max_weekly_classes=max_weekly_classes,
                preferred_times=preferred_times,
                available_days=available_days,
                can_teach_gi=can_teach_gi,
                can_teach_nogi=can_teach_nogi,
                can_teach_open_mat=can_teach_open_mat
            )
            scheduler.add_coach(coach)
            save_scheduler(scheduler)
            flash('Coach added!')
        elif 'edit_coach' in request.form:
            idx = int(request.form['coach_edit_idx'])
            coach = scheduler.coaches[idx]
            coach.name = request.form['coach_name'].strip()
            coach.max_weekly_classes = int(request.form['coach_max_weekly_classes'])
            coach.preferred_times = request.form.getlist('coach_preferred_times')
            coach.available_days = request.form.getlist('coach_available_days')
            coach.can_teach_gi = 'coach_can_teach_gi' in request.form
            coach.can_teach_nogi = 'coach_can_teach_nogi' in request.form
            coach.can_teach_open_mat = 'coach_can_teach_open_mat' in request.form
            save_scheduler(scheduler)
            flash('Coach updated!')
        elif 'delete_coach' in request.form:
            idx = int(request.form['coach_delete_idx'])
            del scheduler.coaches[idx]
            save_scheduler(scheduler)
            flash('Coach deleted!')
        elif 'start_edit_coach' in request.form:
            coach_edit_idx = int(request.form['coach_edit_idx'])
            coach_edit_data = scheduler.coaches[coach_edit_idx]
        # Time Slot CRUD
        if 'add_slot' in request.form:
            from src.models.data_classes import TimeSlot
            from datetime import time
            day = request.form['slot_day']
            start_hour = int(request.form['slot_start_hour'])
            start_minute = int(request.form['slot_start_minute'])
            end_hour = int(request.form['slot_end_hour'])
            end_minute = int(request.form['slot_end_minute'])
            primary_preference = request.form.get('slot_primary_preference')
            secondary_preference = request.form.get('slot_secondary_preference')
            if primary_preference == 'none': primary_preference = None
            if secondary_preference == 'none': secondary_preference = None
            slot = TimeSlot(
                day=day,
                start_time=time(start_hour, start_minute),
                end_time=time(end_hour, end_minute),
                primary_preference=primary_preference,
                secondary_preference=secondary_preference
            )
            scheduler.time_slots.append(slot)
            save_scheduler(scheduler)
            flash('Time slot added!')
        elif 'edit_slot' in request.form:
            from src.models.data_classes import TimeSlot
            from datetime import time
            idx = int(request.form['slot_edit_idx'])
            day = request.form['slot_day']
            start_hour = int(request.form['slot_start_hour'])
            start_minute = int(request.form['slot_start_minute'])
            end_hour = int(request.form['slot_end_hour'])
            end_minute = int(request.form['slot_end_minute'])
            primary_preference = request.form.get('slot_primary_preference')
            secondary_preference = request.form.get('slot_secondary_preference')
            if primary_preference == 'none': primary_preference = None
            if secondary_preference == 'none': secondary_preference = None
            slot = TimeSlot(
                day=day,
                start_time=time(start_hour, start_minute),
                end_time=time(end_hour, end_minute),
                primary_preference=primary_preference,
                secondary_preference=secondary_preference
            )
            scheduler.time_slots[idx] = slot
            save_scheduler(scheduler)
            flash('Time slot updated!')
        elif 'delete_slot' in request.form:
            idx = int(request.form['slot_delete_idx'])
            del scheduler.time_slots[idx]
            save_scheduler(scheduler)
            flash('Time slot deleted!')
        elif 'start_edit_slot' in request.form:
            slot_edit_idx = int(request.form['slot_edit_idx'])
            slot_edit_data = scheduler.time_slots[slot_edit_idx]
        # Class Type CRUD
        if 'add_class_type' in request.form:
            from src.models.data_classes import ClassDefinition
            from src.models.enums import ClassType
            name = request.form['class_type_name'].strip()
            class_type = ClassType(request.form['class_type_type'])
            duration_minutes = int(request.form['class_type_duration'])
            weekly_count = int(request.form['class_type_weekly_count'])
            class_def = ClassDefinition(
                name=name,
                class_type=class_type,
                duration_minutes=duration_minutes,
                weekly_count=weekly_count
            )
            scheduler.add_class_definition(class_def)
            save_scheduler(scheduler)
            flash('Class type added!')
        elif 'edit_class_type' in request.form:
            from src.models.enums import ClassType
            from src.models.data_classes import ClassDefinition
            idx = int(request.form['class_type_edit_idx'])
            # Create a new ClassDefinition instead of modifying the existing one (since it's frozen)
            new_class_def = ClassDefinition(
                name=request.form['class_type_name'].strip(),
                class_type=ClassType(request.form['class_type_type']),
                duration_minutes=int(request.form['class_type_duration']),
                weekly_count=int(request.form['class_type_weekly_count'])
            )
            scheduler.class_definitions[idx] = new_class_def
            save_scheduler(scheduler)
            flash('Class type updated!')
        elif 'delete_class_type' in request.form:
            idx = int(request.form['class_type_delete_idx'])
            del scheduler.class_definitions[idx]
            save_scheduler(scheduler)
            flash('Class type deleted!')
        elif 'start_edit_class_type' in request.form:
            class_edit_idx = int(request.form['class_type_edit_idx'])
            class_edit_data = scheduler.class_definitions[class_edit_idx]
        if 'add_manual' in request.form:
            class_idx = int(request.form['manual_class'])
            coach_idx = int(request.form['manual_coach'])
            slot_idx = int(request.form['manual_slot'])
            ma = {
                'class_name': class_options[class_idx].name,
                'class_type': class_options[class_idx].class_type.value,
                'duration': class_options[class_idx].duration_minutes,
                'coach_name': coach_options[coach_idx].name,
                'slot_idx': slot_idx
            }
            manual_assignments.append(ma)
            session['manual_assignments'] = manual_assignments
            flash('Manual assignment added!')
        elif 'clear_manual' in request.form:
            manual_assignments = []
            session['manual_assignments'] = manual_assignments
            flash('Manual assignments cleared!')
        elif 'generate_schedule' in request.form:
            from src.models.data_classes import ClassDefinition, Coach, TimeSlot
            from src.models.enums import ClassType
            mas = []
            for ma in manual_assignments:
                class_def = next((cd for cd in scheduler.class_definitions if cd.name == ma['class_name']), None)
                coach = next((c for c in scheduler.coaches if c.name == ma['coach_name']), None)
                slot = scheduler.time_slots[ma['slot_idx']]
                if class_def and coach and slot:
                    mas.append({'class_def': class_def, 'coach': coach, 'time_slot': slot})
            schedule_objs, conflicts = scheduler.generate_schedule(manual_assignments=mas)
            day_order = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
            def sc_to_dict(sc, schedule_list):
                same_slot = [s for s in schedule_list if s.time_slot == sc.time_slot]
                same_slot.sort(key=lambda x: x.slot_position)
                idx = sc.slot_position
                from datetime import timedelta, datetime as dt
                slot_start = dt.combine(dt.today(), sc.time_slot.start_time)
                class_start = slot_start
                for prev in same_slot[:idx]:
                    class_start += timedelta(minutes=prev.class_def.duration_minutes)
                class_end = class_start + timedelta(minutes=sc.class_def.duration_minutes)
                return {
                    'class_name': sc.class_def.name,
                    'class_type': sc.class_def.class_type.value,
                    'duration': sc.class_def.duration_minutes,
                    'day': sc.time_slot.day,
                    'start_time': class_start.time().strftime('%H:%M'),
                    'end_time': class_end.time().strftime('%H:%M'),
                    'coach': sc.coach.name,
                    'is_fixed': sc.is_fixed
                }
            schedule_dicts = [sc_to_dict(sc, schedule_objs) for sc in schedule_objs]
            schedule_dicts.sort(key=lambda x: (day_order.index(x['day'].lower()), x['start_time']))
            schedule = schedule_dicts
            session['last_schedule'] = schedule
            session['last_conflicts'] = conflicts
        # TODO: handle config modals, save/upload
    return render_template('unified_scheduler.html',
        coaches=scheduler.coaches,
        time_slots=scheduler.time_slots,
        class_types=scheduler.class_definitions,
        manual_assignments=manual_assignments,
        class_options=class_options,
        coach_options=coach_options,
        slot_options=slot_options,
        schedule=schedule,
        conflicts=conflicts,
        coach_edit_idx=coach_edit_idx,
        coach_edit_data=coach_edit_data,
        slot_edit_idx=slot_edit_idx,
        slot_edit_data=slot_edit_data,
        class_edit_idx=class_edit_idx,
        class_edit_data=class_edit_data
    )

@app.route('/schedule/export/ical')
def export_ical():
    scheduler = get_scheduler()
    schedule = session.get('last_schedule')
    if not schedule:
        flash('No schedule to export!')
        return redirect(url_for('schedule'))
    # Rebuild ScheduledClass objects for export
    from src.models.data_classes import ClassDefinition, TimeSlot, Coach, ScheduledClass
    from src.models.enums import ClassType
    from datetime import time
    schedule_objs = []
    for sc in schedule:
        class_def = ClassDefinition(sc['class_name'], ClassType(sc['class_type']), sc['duration'])
        time_slot = TimeSlot(sc['day'], time.fromisoformat(sc['start_time']), time.fromisoformat(sc['end_time']))
        coach = Coach(sc['coach'], 0, [], [])
        schedule_objs.append(ScheduledClass(class_def, time_slot, coach, is_fixed=sc['is_fixed']))
    ical_str = scheduler.export_to_icalendar(schedule_objs, start_date=date.today(), weeks=4)
    return send_file(
        io.BytesIO(ical_str.encode('utf-8')),
        mimetype='text/calendar',
        as_attachment=True,
        download_name='bjj_schedule.ics'
    )

@app.route('/schedule/export/csv')
def export_csv():
    import csv
    scheduler = get_scheduler()
    schedule = session.get('last_schedule')
    if not schedule:
        flash('No schedule to export!')
        return redirect(url_for('schedule'))
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Class Name', 'Type', 'Duration', 'Day', 'Start Time', 'End Time', 'Coach', 'Fixed'])
    for sc in schedule:
        writer.writerow([
            sc['class_name'], sc['class_type'], sc['duration'], sc['day'],
            sc['start_time'], sc['end_time'], sc['coach'], 'Yes' if sc['is_fixed'] else ''
        ])
    return send_file(
        io.BytesIO(output.getvalue().encode('utf-8')),
        mimetype='text/csv',
        as_attachment=True,
        download_name='bjj_schedule.csv'
    )

if __name__ == '__main__':
    app.run(debug=True) 