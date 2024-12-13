from flask import render_template, flash, jsonify, redirect, request, url_for
from app.modules.community import community_bp  # Ensure community_bp is imported
from flask_login import current_user, login_required
from app.modules.community.forms import CommunityForm
from app.modules.community.models import Community
from app.modules.community.services import CommunityService
from app import db

community_service = CommunityService()


@community_bp.route('/community', methods=['GET'])
def list_communities():
    """List all communities for the current user."""
    all_communities = community_service.get_all()
    sorted_communities = []

    if current_user.is_authenticated:
        # Organize communities based on user ownership and membership
        owner_communities = [
            c for c in all_communities if c.owner_id == current_user.id
        ]
        member_communities = [
            c for c in all_communities if c.owner_id != current_user.id and current_user in c.members
        ]
        other_communities = [
            c for c in all_communities if c.owner_id != current_user.id and current_user not in c.members
        ]

        # Combine lists for display
        sorted_communities = (
            owner_communities + member_communities + other_communities
        )
    else:
        # Display all communities for unauthenticated users
        sorted_communities = all_communities

    return render_template('community/index.html', communities=sorted_communities)


@community_bp.route('/community/create', methods=['GET', 'POST'])
@login_required
def add_community():
    """Create a new community."""
    form = CommunityForm()
    if form.validate_on_submit():
        result = community_service.create(
            name=form.name.data,
            description=form.description.data,
            owner_id=current_user.id
        )
        return community_service.handle_service_response(
            result=result,
            errors=form.errors,
            success_url_redirect='community.list_communities',
            success_msg='Community created successfully!',
            error_template='community/create.html',
            form=form
        )
    return render_template('community/create.html', form=form)


@community_bp.route('/community/delete/<int:community_id>', methods=['POST'])
@login_required
def remove_community(community_id):
    """Delete a community."""
    community = community_service.get_or_404(community_id)

    # Ensure the user is the owner before deletion
    if community.owner_id != current_user.id:
        flash("You are not authorized to delete this community.", "danger")
        return redirect(url_for('community.list_communities'))

    # Clear member relationships and delete the community
    community.members.clear()
    db.session.commit()
    db.session.delete(community)
    db.session.commit()
    flash("Community deleted successfully.", "success")
    return redirect(url_for('community.list_communities'))


@community_bp.route('/community/edit/<int:community_id>', methods=['GET', 'POST'])
@login_required
def update_community(community_id):
    """Update an existing community."""
    community = community_service.get_or_404(community_id)
    if community.owner_id != current_user.id:
        flash('You are not authorized to edit this community', 'error')
        return redirect(url_for('community.list_communities'))

    form = CommunityForm(obj=community)
    if form.validate_on_submit():
        result = community_service.update(
            community_id,
            name=form.name.data,
            description=form.description.data
        )
        return community_service.handle_service_response(
            result=result,
            errors=form.errors,
            success_url_redirect='community.list_communities',
            success_msg='Community updated successfully!',
            error_template='community/edit.html',
            form=form
        )
    return render_template('community/edit.html', form=form, community=community)


@community_bp.route('/community/<int:community_id>', methods=['GET'])
def view_community(community_id):
    """View a specific community."""
    community = community_service.get_or_404(community_id)
    datasets = community.shared_datasets
    return render_template('community/show.html', community=community, datasets=datasets)


@community_bp.route('/community/join', methods=['POST'])
@login_required
def join_community():
    """Join a community."""
    community_id = request.json.get('community_id')
    if not community_id:
        return jsonify({'error': 'Community ID is required'}), 400

    community = Community.query.get(community_id)
    if not community:
        return jsonify({'error': 'Community not found'}), 404

    if community.owner_id == current_user.id:
        return jsonify({'error': 'You are the owner of this community'}), 403

    if current_user in community.members:
        return jsonify({'error': 'You are already a member of this community'}), 403

    community.members.append(current_user)
    db.session.commit()
    return jsonify({'message': 'You have successfully joined the community'})


@community_bp.route('/community/leave', methods=['POST'])
@login_required
def leave_community():
    """Leave a community."""
    community_id = request.json.get('community_id')
    community = community_service.get_or_404(community_id)

    if not community:
        return jsonify({'error': 'Community not found'}), 404

    if current_user not in community.members:
        return jsonify({'error': 'You are not a member of this community'}), 400

    community.members.remove(current_user)
    db.session.commit()
    return jsonify({'message': 'You have successfully left the community'})
