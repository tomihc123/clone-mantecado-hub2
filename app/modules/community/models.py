from app import db


# tabla intermedia para asociación comunidad con usuaario y evitar asocuiaciones Many2Many
community_members = db.Table('community_members',
                             db.Column('community_id', db.Integer, db.ForeignKey('community.id'), primary_key=True),
                             db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True)
                             )


class Community(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text, nullable=False)
    owner_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

    owner = db.relationship("User", back_populates="owned_communities", lazy=True)
    members = db.relationship(
        'User',
        secondary=community_members,
        back_populates='joined_communities'
    )

    datasets = db.relationship('DataSet', backref='community_datasets', lazy=True)
