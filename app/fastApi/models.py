# -----
# =============================================================================
# BABILLAGES — SQLAlchemy Models
# Compatible : FastAPI + SQLAlchemy 2.x + PostgreSQL (Railway)
# Conventions :
#   - BigInteger IDENTITY pour toutes les PKs
#   - Nullable=True par défaut sauf mention contraire (mirror du SQL)
#   - server_default=func.now() pour les timestamps gérés côté DB
#   - Enums Python alignés sur les types PostgreSQL
#   - Relationships déclarées sur toutes les FK pour faciliter les joins
# =============================================================================

from __future__ import annotations

import enum
from typing import List, Optional

from sqlalchemy import (
    BigInteger,
    Boolean,
    CheckConstraint,
    Column,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    SmallInteger,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, TIMESTAMP
from sqlalchemy.orm import DeclarativeBase, relationship, Mapped
from sqlalchemy.sql import func, text


# =============================================================================
# BASE
# =============================================================================

class Base(DeclarativeBase):
    __allow_unmapped__ = True #  remove for production + fix foreignkeys 


# =============================================================================
# ENUMS
# Alignés exactement sur les CREATE TYPE PostgreSQL du schéma
# =============================================================================

class AuthProviderEnum(str, enum.Enum):
    apple     = "apple"
    google    = "google"
    anonymous = "anonymous"


class ModerationStatusEnum(str, enum.Enum):
    pending  = "pending"
    approved = "approved"
    rejected = "rejected"
    flagged  = "flagged"
    archived = "archived"


class ModerationMethodEnum(str, enum.Enum):
    ai_auto    = "ai_auto"
    ai_assisted = "ai_assisted"
    manual     = "manual"


class RejectionReasonEnum(str, enum.Enum):
    inappropriate_content = "inappropriate_content"
    child_safety          = "child_safety"
    spam                  = "spam"
    not_authentic         = "not_authentic"
    off_topic             = "off_topic"
    too_short             = "too_short"
    advertising           = "advertising"
    other                 = "other"


class ReportReasonEnum(str, enum.Enum):
    inappropriate = "inappropriate"
    spam          = "spam"
    fake          = "fake"
    child_safety  = "child_safety"
    copyright     = "copyright"
    other         = "other"


class ReportStatusEnum(str, enum.Enum):
    pending   = "pending"
    reviewed  = "reviewed"
    actioned  = "actioned"
    dismissed = "dismissed"


class IapProductEnum(str, enum.Enum):
    pdf_one_shot    = "pdf_one_shot"
    premium_annual  = "premium_annual"


class IapStatusEnum(str, enum.Enum):
    pending   = "pending"
    completed = "completed"
    refunded  = "refunded"
    expired   = "expired"
    cancelled = "cancelled"


class NotificationTypeEnum(str, enum.Enum):
    daily_pepite    = "daily_pepite"
    vote_milestone  = "vote_milestone"
    approved        = "approved"
    rejected        = "rejected"
    new_top_monthly = "new_top_monthly"
    system          = "system"

# =============================================================================
# TABLE : users
# Utilisateurs ayant créé un compte (Apple/Google Sign-In)
# =============================================================================

class User(Base):
    __tablename__ = "users"

    # PK — BIGINT GENERATED ALWAYS AS IDENTITY
    id = Column(BigInteger, primary_key=True, autoincrement=True)

    # Authentification
    auth_provider    = Column(
        String,           # stocké comme TEXT, cast vers l'enum en Python
        nullable=False,
    )
    provider_user_id = Column(Text, nullable=False)             # ID fourni par Apple/Google
    email            = Column(Text, nullable=True)              # Peut être null (Apple masque parfois)
    email_verified   = Column(Boolean, server_default="false", nullable=False)

    # Profil
    display_name = Column(Text, nullable=True)                  # Optionnel, non affiché publiquement
    avatar_color = Column(Text, server_default="#F5C842", nullable=False)

    # Statut du compte
    is_active  = Column(Boolean, server_default="true",  nullable=False)
    is_banned  = Column(Boolean, server_default="false", nullable=False)
    ban_reason = Column(Text, nullable=True)
    banned_at  = Column(TIMESTAMP(timezone=True), nullable=True)

    # Premium
    is_premium         = Column(Boolean, server_default="false", nullable=False)
    premium_expires_at = Column(TIMESTAMP(timezone=True), nullable=True)  # NULL = pas de premium actif

    # Préférences
    locale                = Column(Text, server_default="fr", nullable=False)
    push_token            = Column(Text, nullable=True)          # Token Expo Push Notifications
    notif_daily_pepite    = Column(Boolean, server_default="true", nullable=False)
    notif_vote_milestone  = Column(Boolean, server_default="true", nullable=False)
    notif_moderation      = Column(Boolean, server_default="true", nullable=False)

    # RGPD
    gdpr_consent_at              = Column(TIMESTAMP(timezone=True), nullable=True)
    gdpr_version                 = Column(Text, nullable=True)
    data_export_requested_at     = Column(TIMESTAMP(timezone=True), nullable=True)
    data_deletion_requested_at   = Column(TIMESTAMP(timezone=True), nullable=True)

    # Timestamps
    created_at   = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
    updated_at   = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
    last_seen_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
    deleted_at   = Column(TIMESTAMP(timezone=True), nullable=True)  # Soft delete

    # Constraints
    __table_args__ = (
        UniqueConstraint("auth_provider", "provider_user_id", name="users_provider_unique"),
        # CheckConstraint sur le format email géré côté PostgreSQL, pas besoin de le répliquer en Python
    )

    # Relationships

    devices: Mapped[list["Device"]] = relationship(  # type: ignore
        "Device",
        back_populates="user",
        foreign_keys="Device.user_id"
    )

    quotes: Mapped[list["Quote"]] = relationship(
        "Quote",
        back_populates="user",
        foreign_keys="Quote.user_id"
    )

    votes: Mapped[list["Vote"]] = relationship(
        "Vote",
        back_populates="user"
    )

    reports_filed: Mapped[list["Report"]] = relationship(
        "Report",
        back_populates="user",
        foreign_keys="Report.user_id"
    )
    
    iap_purchases: Mapped[list["IapPurchase"]] = relationship(
        "IapPurchase",
        back_populates="user"
    )

    pdf_booklets: Mapped[list["PdfBooklet"]] = relationship(
        "PdfBooklet",
        back_populates="user"
    )

    notifications: Mapped[list["Notification"]] = relationship(
        "Notification",
        back_populates="user"
    )

    ai_moderation_logs: List["AiModerationLog"] = relationship(
        "AiModerationLog",
        back_populates="override_user",
        foreign_keys="[AiModerationLog.override_by]"
    )


# =============================================================================
# TABLE : devices
# Appareils anonymes — traçabilité sans compte
# =============================================================================

class Device(Base):
    __tablename__ = "devices"

    id                 = Column(Text, primary_key=True)
    device_fingerprint = Column(Text, nullable=False, unique=True)   # Hash anonymisé de l'appareil
    user_id            = Column(BigInteger, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    locale             = Column(Text, server_default="fr", nullable=False)
    platform           = Column(Text, nullable=True)                 # 'ios' ou 'android'
    app_version        = Column(Text, nullable=True)
    created_at         = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
    last_seen_at       = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)

    # Relationships

    user: Mapped[Optional["User"]] = relationship(
        "User",
        back_populates="devices",
        foreign_keys=[user_id]
    )

    quotes: Mapped[list["Quote"]] = relationship(
        "Quote",
        back_populates="device",
        foreign_keys="Quote.device_id"
    )
    reports: Mapped[list["Report"]] = relationship(
        "Report",
        back_populates="device",
        foreign_keys="Report.device_id"
    )

    analytics_events: Mapped[list["AnalyticsEvent"]] = relationship(
        "AnalyticsEvent",
        back_populates="device"
    )

    votes: Mapped[list["Vote"]] = relationship(
        "Vote",
        back_populates="device",
        foreign_keys="Vote.device_id"
    )


# =============================================================================
# TABLE : quotes
# Table centrale — les pépites soumises par la communauté
# =============================================================================

class Quote(Base):
    __tablename__ = "quotes"

    id        = Column(BigInteger, primary_key=True, autoincrement=True)

    # Auteur (l'un ou l'autre doit être non-null — vérifié par constraint SQL)
    user_id   = Column(BigInteger, ForeignKey("users.id",   ondelete="SET NULL"), nullable=True)
    device_id = Column(Text, ForeignKey("devices.id", ondelete="SET NULL"), nullable=True)

    # Contenu
    child_name       = Column(Text,         nullable=False)          # Prénom ou surnom
    child_age_years  = Column(SmallInteger, nullable=False)          # Âge en années (0-12)
    child_age_months = Column(SmallInteger, server_default="0", nullable=False)  # Mois supplémentaires
    quote            = Column(Text,         nullable=False)          # La phrase de l'enfant (5-800 chars)
    context          = Column(Text,         nullable=True)           # Contexte optionnel
    language         = Column(Text,         server_default="fr", nullable=False)

    # Modération
    status            = Column(String,  server_default="pending", nullable=False)
    moderation_method = Column(String,  nullable=True)
    rejection_reason  = Column(String,  nullable=True)
    moderation_notes  = Column(Text,    nullable=True)
    moderated_at      = Column(TIMESTAMP(timezone=True), nullable=True)
    moderated_by      = Column(BigInteger, ForeignKey("users.id"), nullable=True)

    # Scores IA (0.0 à 1.0)
    ai_safety_score  = Column(Numeric(4, 3), nullable=True)
    ai_quality_score = Column(Numeric(4, 3), nullable=True)
    ai_category_tags = Column(ARRAY(Text),   nullable=True)          # ['philosophique', 'humour', ...]

    # Scores de classement (précalculés par cron jobs)
    vote_count      = Column(Integer,        server_default="0", nullable=False)
    report_count    = Column(Integer,        server_default="0", nullable=False)
    trending_score  = Column(Numeric(12, 4), server_default="0", nullable=False)
    bayesian_score  = Column(Numeric(12, 4), server_default="0", nullable=False)

    # Publication
    published_at = Column(TIMESTAMP(timezone=True), nullable=True)   # NULL jusqu'à approbation

    # Archive 2013
    is_archive   = Column(Boolean,      server_default="false", nullable=False)
    archive_year = Column(SmallInteger, nullable=True)

    # Timestamps
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
    deleted_at = Column(TIMESTAMP(timezone=True), nullable=True)     # Soft delete

    __table_args__ = (
        CheckConstraint("child_age_years BETWEEN 0 AND 18",             name="quotes_age_range"),
        CheckConstraint("child_age_months BETWEEN 0 AND 11",            name="quotes_age_months"),
        CheckConstraint("char_length(quote) BETWEEN 5 AND 800",         name="quotes_quote_length"),
        CheckConstraint("user_id IS NOT NULL OR device_id IS NOT NULL", name="quotes_author"),
    )

    # Relationships
    user: Mapped[Optional["User"]] = relationship(
        "User",
        back_populates="quotes",
        foreign_keys=[user_id]
    )

    device: Mapped[Optional["Device"]] = relationship(
        "Device",
        back_populates="quotes",
        foreign_keys=[device_id]
    )

    moderator: Mapped[Optional["User"]] = relationship(
        "User",
        foreign_keys=[moderated_by]
    )

    votes: Mapped[list["Vote"]] = relationship(
        "Vote",
        back_populates="quote",
        cascade="all, delete-orphan"
    )

    reports: Mapped[list["Report"]] = relationship(
        "Report",
        back_populates="quote",
        cascade="all, delete-orphan"
    )

    ai_logs: Mapped[list["AiModerationLog"]] = relationship(
        "AiModerationLog",
        back_populates="quote",
        cascade="all, delete-orphan"
    )

    monthly_rankings: Mapped[list["MonthlyRanking"]] = relationship(
        "MonthlyRanking",
        back_populates="quote"
    )

    analytics_events: Mapped[list["AnalyticsEvent"]] = relationship(
        "AnalyticsEvent",
        back_populates="quote"
    )


# =============================================================================
# TABLE : votes
# Un vote par utilisateur connecté par quote (toutes sessions confondues)
# =============================================================================

class Vote(Base):
    __tablename__ = "votes"

    id          = Column(BigInteger, primary_key=True, autoincrement=True)
    quote_id    = Column(BigInteger, ForeignKey("quotes.id", ondelete="CASCADE"),  nullable=False)
    user_id     = Column(BigInteger, ForeignKey("users.id",  ondelete="CASCADE"),  nullable=True)   # connecté
    device_id   = Column(Text,       ForeignKey("devices.id", ondelete="CASCADE"), nullable=True)   # non connecté
    vote_period = Column(Text, nullable=False)                       # Format : 'YYYY-MM'
    created_at  = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)

    __table_args__ = (
        CheckConstraint("(user_id IS NOT NULL) <> (device_id IS NOT NULL)", name="votes_user_or_device"),
        Index("votes_unique_user", "quote_id", "user_id", unique=True, postgresql_where=text("user_id IS NOT NULL")),
        Index("votes_unique_device", "quote_id", "device_id", unique=True, postgresql_where=text("device_id IS NOT NULL")),
    )

    # Relationships
    quote: Mapped["Quote"] = relationship(
        "Quote",
        back_populates="votes"
    )
    user: Mapped[Optional["User"]] = relationship(
        "User",
        back_populates="votes",
        foreign_keys=[user_id]
    )
    device: Mapped[Optional["Device"]] = relationship(
        "Device",
        back_populates="votes",
        foreign_keys=[device_id]
    )


# =============================================================================
# TABLE : monthly_rankings
# Snapshots mensuels figés en fin de mois
# =============================================================================

class MonthlyRanking(Base):
    __tablename__ = "monthly_rankings"

    id           = Column(BigInteger, primary_key=True, autoincrement=True)
    period       = Column(Text,       nullable=False)               # 'YYYY-MM'
    quote_id     = Column(BigInteger, ForeignKey("quotes.id"), nullable=False)
    rank         = Column(Integer,  nullable=False)
    vote_count   = Column(Integer,  nullable=False)                 # Votes sur la période uniquement
    is_finalized = Column(Boolean,  server_default="false", nullable=False)  # TRUE = snapshot figé
    created_at   = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)

    __table_args__ = (
        UniqueConstraint("period", "quote_id", name="monthly_rankings_unique"),
    )

    # Relationships
    quote: Mapped["Quote"] = relationship(
        "Quote",
        back_populates="monthly_rankings"
    )


# =============================================================================
# TABLE : reports
# Signalements de contenu par les utilisateurs
# =============================================================================

class Report(Base):
    __tablename__ = "reports"

    id          = Column(BigInteger, primary_key=True, autoincrement=True)
    quote_id    = Column(BigInteger, ForeignKey("quotes.id",   ondelete="CASCADE"),  nullable=False)
    user_id     = Column(BigInteger, ForeignKey("users.id",    ondelete="SET NULL"), nullable=True)
    device_id   = Column(Text, ForeignKey("devices.id",  ondelete="SET NULL"), nullable=True)

    reason       = Column(String, nullable=False)
    details      = Column(Text,   nullable=True)
    status       = Column(String, server_default="pending", nullable=False)
    reviewed_by  = Column(BigInteger, ForeignKey("users.id"), nullable=True)
    reviewed_at  = Column(TIMESTAMP(timezone=True), nullable=True)
    action_taken = Column(Text, nullable=True)

    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)

    __table_args__ = (
        UniqueConstraint("quote_id", "user_id",   name="reports_unique_user",   deferrable=True),
        UniqueConstraint("quote_id", "device_id", name="reports_unique_device", deferrable=True),
        CheckConstraint("user_id IS NOT NULL OR device_id IS NOT NULL", name="reports_author"),
    )

    # Relationships
    quote: Mapped["Quote"] = relationship(
        "Quote",
        back_populates="reports",
        foreign_keys=[quote_id]
    )
    user: Mapped[Optional["User"]] = relationship(
        "User",
        back_populates="reports_filed",
        foreign_keys=[user_id]
    )
    device: Mapped[Optional["Device"]] = relationship(
        "Device",
        back_populates="reports",
        foreign_keys=[device_id]
    )


# =============================================================================
# TABLE : ai_moderation_logs
# Journal complet de toutes les décisions IA (traçabilité + monitoring coûts)
# =============================================================================

class AiModerationLog(Base):
    __tablename__ = "ai_moderation_logs"

    id       = Column(BigInteger, primary_key=True, autoincrement=True)
    quote_id = Column(BigInteger, ForeignKey("quotes.id", ondelete="CASCADE"), nullable=False)

    # Modèle utilisé
    ai_model         = Column(Text, nullable=False)                 # Ex : 'gpt-4o-mini'
    ai_model_version = Column(Text, nullable=True)

    # Tokens & coût
    prompt_tokens     = Column(Integer, nullable=True)
    completion_tokens = Column(Integer, nullable=True)
    cost_usd          = Column(Numeric(10, 6), nullable=True)       # Monitoring budget OpenAI

    # Décision IA
    decision         = Column(String,         nullable=False)       # ModerationStatusEnum
    safety_score     = Column(Numeric(4, 3),  nullable=True)
    quality_score    = Column(Numeric(4, 3),  nullable=True)
    suggested_tags   = Column(ARRAY(Text),    nullable=True)
    rejection_reason = Column(String,         nullable=True)
    reasoning        = Column(Text,           nullable=True)        # Explication de la décision

    # Override humain
    was_overridden   = Column(Boolean, server_default="false", nullable=False)
    override_by      = Column(BigInteger, ForeignKey("users.id"), nullable=True)
    override_at      = Column(TIMESTAMP(timezone=True), nullable=True)
    override_decision = Column(String, nullable=True)

    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    quote: Mapped["Quote"] = relationship(
        "Quote",
        back_populates="ai_logs"
    )

    override_user: Optional["User"] = relationship(
        "User",
        back_populates="ai_moderation_logs",
        foreign_keys="[AiModerationLog.override_by]"
    )


# =============================================================================
# TABLE : iap_purchases
# Historique des achats in-app (PDF one-shot + abonnement Premium annuel)
# =============================================================================

class IapPurchase(Base):
    __tablename__ = "iap_purchases"

    id      = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    # Produit
    product  = Column(String, nullable=False)                       # IapProductEnum
    platform = Column(Text,   nullable=False)                       # 'ios' ou 'android'

    # Identifiants stores
    transaction_id          = Column(Text, nullable=False, unique=True)   # ID Apple/Google
    original_transaction_id = Column(Text, nullable=True)           # Pour les renouvellements
    receipt_data            = Column(Text, nullable=True)           # Reçu brut pour validation

    # Prix
    price_usd   = Column(Numeric(10, 2), nullable=True)
    price_local = Column(Numeric(10, 2), nullable=True)
    currency    = Column(Text, server_default="EUR", nullable=False)

    # Statut
    status = Column(String, server_default="pending", nullable=False)  # IapStatusEnum

    # Abonnement (premium_annual uniquement)
    subscription_start = Column(TIMESTAMP(timezone=True), nullable=True)
    subscription_end   = Column(TIMESTAMP(timezone=True), nullable=True)
    is_trial           = Column(Boolean, server_default="false", nullable=False)
    renewal_count      = Column(Integer, server_default="0",     nullable=False)

    # PDF (pdf_one_shot uniquement)
    pdf_generated_at   = Column(TIMESTAMP(timezone=True), nullable=True)
    pdf_download_url   = Column(Text,    nullable=True)             # URL signée temporaire
    pdf_download_count = Column(Integer, server_default="0", nullable=False)

    # Timestamps
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    user: Mapped["User"] = relationship(
        "User",
        back_populates="iap_purchases"
    )

    pdf_booklets: Mapped[list["PdfBooklet"]] = relationship(
        "PdfBooklet",
        back_populates="purchase"
    )

# =============================================================================
# TABLE : pdf_booklets
# Livrets PDF générés à la demande (one-shot ou premium illimité)
# =============================================================================

class PdfBooklet(Base):
    __tablename__ = "pdf_booklets"

    id          = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id     = Column(BigInteger, ForeignKey("users.id",         ondelete="CASCADE"), nullable=False)
    purchase_id = Column(BigInteger, ForeignKey("iap_purchases.id"), nullable=True)      # NULL si premium

    # Contenu du livret
    quote_ids      = Column(ARRAY(BigInteger), nullable=False)      # IDs des quotes incluses
    anecdote_count = Column(Integer, nullable=False)
    child_name     = Column(Text, nullable=True)                    # Prénom sur la couverture
    title          = Column(Text, nullable=True)                    # Titre personnalisé

    # Génération
    status              = Column(Text, server_default="pending", nullable=False)  # pending/generating/ready/error
    error_message       = Column(Text,    nullable=True)
    file_size_bytes     = Column(Integer, nullable=True)
    storage_path        = Column(Text,    nullable=True)            # Chemin Railway volumes / S3
    download_url        = Column(Text,    nullable=True)            # URL signée temporaire
    download_expires_at = Column(TIMESTAMP(timezone=True), nullable=True)
    download_count      = Column(Integer, server_default="0", nullable=False)

    # Timestamps
    created_at   = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
    generated_at = Column(TIMESTAMP(timezone=True), nullable=True)

    # Relationships
    user: Mapped["User"] = relationship(
        "User",
        back_populates="pdf_booklets"
    )

    purchase: Mapped[Optional["IapPurchase"]] = relationship(
        "IapPurchase",
        back_populates="pdf_booklets"
    )


# =============================================================================
# TABLE : notifications
# Notifications push Expo envoyées aux utilisateurs
# =============================================================================

class Notification(Base):
    __tablename__ = "notifications"

    id      = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    type  = Column(String, nullable=False)                          # NotificationTypeEnum
    title = Column(Text,   nullable=False)
    body  = Column(Text,   nullable=False)
    data  = Column(JSONB,  nullable=True)                           # Payload custom (quote_id, etc.)

    # Statut
    sent_at    = Column(TIMESTAMP(timezone=True), nullable=True)
    is_sent    = Column(Boolean, server_default="false", nullable=False)
    send_error = Column(Text,    nullable=True)
    is_read    = Column(Boolean, server_default="false", nullable=False)
    read_at    = Column(TIMESTAMP(timezone=True), nullable=True)

    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    user: Mapped["User"] = relationship(
        "User",
        back_populates="notifications"
    )


# =============================================================================
# TABLE : app_config
# Configuration dynamique sans redéploiement (clé/valeur)
# =============================================================================

class AppConfig(Base):
    __tablename__ = "app_config"

    key         = Column(Text, primary_key=True)
    value       = Column(Text, nullable=False)
    description = Column(Text, nullable=True)
    updated_at  = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)


# =============================================================================
# TABLE : analytics_events
# Événements custom backend — complément Firebase Analytics
# Rétention 90 jours via purge_old_analytics_events() (cron hebdo)
# =============================================================================

class AnalyticsEvent(Base):
    __tablename__ = "analytics_events"

    id         = Column(BigInteger, primary_key=True, autoincrement=True)
    event_name = Column(Text, nullable=False, index=True)           # 'quote_viewed', 'vote_cast', etc.
    user_id    = Column(BigInteger, ForeignKey("users.id",    ondelete="SET NULL"), nullable=True)
    device_id  = Column(Text, ForeignKey("devices.id",  ondelete="SET NULL"), nullable=True)
    quote_id   = Column(BigInteger, ForeignKey("quotes.id",   ondelete="SET NULL"), nullable=True)
    properties = Column(JSONB, nullable=True)                       # Propriétés custom de l'événement
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False, index=True)

    # Relationships
    user: Mapped[Optional["User"]] = relationship(
        "User",
        back_populates=None,
        foreign_keys=[user_id]
    )

    device: Mapped[Optional["Device"]] = relationship(
        "Device",
        back_populates="analytics_events",
        foreign_keys=[device_id]
    )

    quote: Mapped[Optional["Quote"]] = relationship(
        "Quote",
        back_populates="analytics_events",
        foreign_keys=[quote_id]
    )
