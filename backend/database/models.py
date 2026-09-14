import uuid
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


# ============================================================
# 01. USERS
# ============================================================

class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
    )

    password_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    # avatar_url: Mapped[str | None] = mapped_column(
    #     Text,
    #     nullable=True,
    # )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
    )

    is_verified: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    last_login_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    sessions = relationship(
        "Session",
        back_populates="user"
    )
    # workspaces = relationship(
    #     "Workspace",
    #     back_populates="owner",
    #     foreign_keys="Workspace.owner_id",
    # )

    # workspace_members = relationship(
    #     "WorkspaceMember",
    #     back_populates="user",
    #     cascade="all, delete-orphan",
    # )

    # projects = relationship(
    #     "Project",
    #     back_populates="creator",
    #     foreign_keys="Project.created_by",
    # )

    # agents = relationship(
    #     "Agent",
    #     back_populates="creator",
    #     foreign_keys="Agent.created_by",
    # )

    # workflows = relationship(
    #     "Workflow",
    #     back_populates="creator",
    #     foreign_keys="Workflow.created_by",
    # )

    # chats = relationship(
    #     "Chat",
    #     back_populates="user",
    #     cascade="all, delete-orphan",
    # )

    # agent_runs = relationship(
    #     "AgentRun",
    #     back_populates="user",
    # )

    # workflow_runs = relationship(
    #     "WorkflowRun",
    #     back_populates="user",
    # )

    # credentials = relationship(
    #     "Credential",
    #     back_populates="user",
    #     cascade="all, delete-orphan",
    # )

    # api_keys = relationship(
    #     "ApiKey",
    #     back_populates="user",
    #     cascade="all, delete-orphan",
    # )

    # activity_logs = relationship(
    #     "ActivityLog",
    #     back_populates="user",
    # )

    # workspace_invitations = relationship(
    #     "WorkspaceInvitation",
    #     back_populates="inviter",
    #     foreign_keys="WorkspaceInvitation.invited_by",
    # )


# ============================================================
# 02. SESSIONS
# ============================================================

class Session(Base):
    __tablename__ = "sessions"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    token_hash: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
    )

    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    last_used_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    # user_agent: Mapped[str | None] = mapped_column(
    #     Text,
    #     nullable=True,
    # )

    # ip_address: Mapped[str | None] = mapped_column(
    #     String(45),
    #     nullable=True,
    # )

    # Relationships
    user = relationship(
        "User",
        back_populates="sessions",
    )


# # ============================================================
# # 03. WORKSPACES
# # ============================================================

# class Workspace(Base):
#     __tablename__ = "workspaces"

#     id: Mapped[uuid.UUID] = mapped_column(
#         UUID(as_uuid=True),
#         primary_key=True,
#         default=uuid.uuid4,
#     )

#     name: Mapped[str] = mapped_column(
#         String(255),
#         nullable=False,
#     )

#     slug: Mapped[str] = mapped_column(
#         String(255),
#         unique=True,
#         nullable=False,
#         index=True,
#     )

#     description: Mapped[str | None] = mapped_column(
#         Text,
#         nullable=True,
#     )

#     owner_id: Mapped[uuid.UUID] = mapped_column(
#         UUID(as_uuid=True),
#         ForeignKey("users.id", ondelete="CASCADE"),
#         nullable=False,
#         index=True,
#     )

#     avatar_url: Mapped[str | None] = mapped_column(
#         Text,
#         nullable=True,
#     )

#     created_at: Mapped[datetime] = mapped_column(
#         DateTime(timezone=True),
#         nullable=False,
#         default=lambda: datetime.now(timezone.utc),
#     )

#     updated_at: Mapped[datetime] = mapped_column(
#         DateTime(timezone=True),
#         nullable=False,
#         default=lambda: datetime.now(timezone.utc),
#         onupdate=lambda: datetime.now(timezone.utc),
#     )

#     # Relationships
#     owner = relationship(
#         "User",
#         back_populates="workspaces",
#         foreign_keys=[owner_id],
#     )

#     workspace_members = relationship(
#         "WorkspaceMember",
#         back_populates="workspace",
#         cascade="all, delete-orphan",
#     )

#     projects = relationship(
#         "Project",
#         back_populates="workspace",
#         cascade="all, delete-orphan",
#     )

#     chats = relationship(
#         "Chat",
#         back_populates="workspace",
#         cascade="all, delete-orphan",
#     )

#     credentials = relationship(
#         "Credential",
#         back_populates="workspace",
#         cascade="all, delete-orphan",
#     )

#     api_keys = relationship(
#         "ApiKey",
#         back_populates="workspace",
#         cascade="all, delete-orphan",
#     )

#     webhooks = relationship(
#         "Webhook",
#         back_populates="workspace",
#         cascade="all, delete-orphan",
#     )

#     activity_logs = relationship(
#         "ActivityLog",
#         back_populates="workspace",
#         cascade="all, delete-orphan",
#     )

#     workspace_invitations = relationship(
#         "WorkspaceInvitation",
#         back_populates="workspace",
#         cascade="all, delete-orphan",
#     )


# # ============================================================
# # 04. WORKSPACE MEMBERS
# # ============================================================

# class WorkspaceMember(Base):
#     __tablename__ = "workspace_members"

#     id: Mapped[uuid.UUID] = mapped_column(
#         UUID(as_uuid=True),
#         primary_key=True,
#         default=uuid.uuid4,
#     )

#     workspace_id: Mapped[uuid.UUID] = mapped_column(
#         UUID(as_uuid=True),
#         ForeignKey("workspaces.id", ondelete="CASCADE"),
#         nullable=False,
#         index=True,
#     )

#     user_id: Mapped[uuid.UUID] = mapped_column(
#         UUID(as_uuid=True),
#         ForeignKey("users.id", ondelete="CASCADE"),
#         nullable=False,
#         index=True,
#     )

#     role: Mapped[str] = mapped_column(
#         String(50),
#         nullable=False,
#         default="viewer",
#     )

#     joined_at: Mapped[datetime] = mapped_column(
#         DateTime(timezone=True),
#         nullable=False,
#         default=lambda: datetime.now(timezone.utc),
#     )

#     __table_args__ = (
#         UniqueConstraint(
#             "workspace_id",
#             "user_id",
#             name="uq_workspace_member",
#         ),
#     )

#     # Relationships
#     workspace = relationship(
#         "Workspace",
#         back_populates="workspace_members",
#     )

#     user = relationship(
#         "User",
#         back_populates="workspace_members",
#     )


# # ============================================================
# # 05. PROJECTS
# # ============================================================

# class Project(Base):
#     __tablename__ = "projects"

#     id: Mapped[uuid.UUID] = mapped_column(
#         UUID(as_uuid=True),
#         primary_key=True,
#         default=uuid.uuid4,
#     )

#     workspace_id: Mapped[uuid.UUID] = mapped_column(
#         UUID(as_uuid=True),
#         ForeignKey("workspaces.id", ondelete="CASCADE"),
#         nullable=False,
#         index=True,
#     )

#     name: Mapped[str] = mapped_column(
#         String(255),
#         nullable=False,
#     )

#     slug: Mapped[str] = mapped_column(
#         String(255),
#         nullable=False,
#     )

#     description: Mapped[str | None] = mapped_column(
#         Text,
#         nullable=True,
#     )

#     created_by: Mapped[uuid.UUID | None] = mapped_column(
#         UUID(as_uuid=True),
#         ForeignKey("users.id", ondelete="SET NULL"),
#         nullable=True,
#         index=True,
#     )

#     created_at: Mapped[datetime] = mapped_column(
#         DateTime(timezone=True),
#         nullable=False,
#         default=lambda: datetime.now(timezone.utc),
#     )

#     updated_at: Mapped[datetime] = mapped_column(
#         DateTime(timezone=True),
#         nullable=False,
#         default=lambda: datetime.now(timezone.utc),
#         onupdate=lambda: datetime.now(timezone.utc),
#     )

#     __table_args__ = (
#         UniqueConstraint(
#             "workspace_id",
#             "slug",
#             name="uq_project_workspace_slug",
#         ),
#     )

#     # Relationships
#     workspace = relationship(
#         "Workspace",
#         back_populates="projects",
#     )

#     creator = relationship(
#         "User",
#         back_populates="projects",
#         foreign_keys=[created_by],
#     )

#     agents = relationship(
#         "Agent",
#         back_populates="project",
#         cascade="all, delete-orphan",
#     )

#     workflows = relationship(
#         "Workflow",
#         back_populates="project",
#         cascade="all, delete-orphan",
#     )

#     chats = relationship(
#         "Chat",
#         back_populates="project",
#     )


# # ============================================================
# # 06. AGENTS
# # ============================================================

# class Agent(Base):
#     __tablename__ = "agents"

#     id: Mapped[uuid.UUID] = mapped_column(
#         UUID(as_uuid=True),
#         primary_key=True,
#         default=uuid.uuid4,
#     )

#     project_id: Mapped[uuid.UUID] = mapped_column(
#         UUID(as_uuid=True),
#         ForeignKey("projects.id", ondelete="CASCADE"),
#         nullable=False,
#         index=True,
#     )

#     name: Mapped[str] = mapped_column(
#         String(255),
#         nullable=False,
#     )

#     slug: Mapped[str] = mapped_column(
#         String(255),
#         nullable=False,
#     )

#     description: Mapped[str | None] = mapped_column(
#         Text,
#         nullable=True,
#     )

#     instructions: Mapped[str] = mapped_column(
#         Text,
#         nullable=False,
#     )

#     model: Mapped[str | None] = mapped_column(
#         String(255),
#         nullable=True,
#     )

#     temperature: Mapped[float | None] = mapped_column(
#         Float,
#         nullable=True,
#     )

#     status: Mapped[str] = mapped_column(
#         String(50),
#         nullable=False,
#         default="active",
#     )

#     created_by: Mapped[uuid.UUID | None] = mapped_column(
#         UUID(as_uuid=True),
#         ForeignKey("users.id", ondelete="SET NULL"),
#         nullable=True,
#         index=True,
#     )

#     created_at: Mapped[datetime] = mapped_column(
#         DateTime(timezone=True),
#         nullable=False,
#         default=lambda: datetime.now(timezone.utc),
#     )

#     updated_at: Mapped[datetime] = mapped_column(
#         DateTime(timezone=True),
#         nullable=False,
#         default=lambda: datetime.now(timezone.utc),
#         onupdate=lambda: datetime.now(timezone.utc),
#     )

#     __table_args__ = (
#         UniqueConstraint(
#             "project_id",
#             "slug",
#             name="uq_agent_project_slug",
#         ),
#     )

#     # Relationships
#     project = relationship(
#         "Project",
#         back_populates="agents",
#     )

#     creator = relationship(
#         "User",
#         back_populates="agents",
#         foreign_keys=[created_by],
#     )

#     versions = relationship(
#         "AgentVersion",
#         back_populates="agent",
#         cascade="all, delete-orphan",
#         order_by="AgentVersion.version_number",
#     )

#     agent_tools = relationship(
#         "AgentTool",
#         back_populates="agent",
#         cascade="all, delete-orphan",
#     )

#     tools = relationship(
#         "Tool",
#         secondary="agent_tools",
#         viewonly=True,
#     )

#     runs = relationship(
#         "AgentRun",
#         back_populates="agent",
#         cascade="all, delete-orphan",
#     )

#     chats = relationship(
#         "Chat",
#         back_populates="agent",
#     )


# # ============================================================
# # 07. AGENT VERSIONS
# # ============================================================

# class AgentVersion(Base):
#     __tablename__ = "agent_versions"

#     id: Mapped[uuid.UUID] = mapped_column(
#         UUID(as_uuid=True),
#         primary_key=True,
#         default=uuid.uuid4,
#     )

#     agent_id: Mapped[uuid.UUID] = mapped_column(
#         UUID(as_uuid=True),
#         ForeignKey("agents.id", ondelete="CASCADE"),
#         nullable=False,
#         index=True,
#     )

#     version_number: Mapped[int] = mapped_column(
#         Integer,
#         nullable=False,
#     )

#     instructions: Mapped[str] = mapped_column(
#         Text,
#         nullable=False,
#     )

#     model: Mapped[str | None] = mapped_column(
#         String(255),
#         nullable=True,
#     )

#     temperature: Mapped[float | None] = mapped_column(
#         Float,
#         nullable=True,
#     )

#     configuration: Mapped[dict[str, Any] | None] = mapped_column(
#         JSONB,
#         nullable=True,
#     )

#     created_by: Mapped[uuid.UUID | None] = mapped_column(
#         UUID(as_uuid=True),
#         ForeignKey("users.id", ondelete="SET NULL"),
#         nullable=True,
#         index=True,
#     )

#     created_at: Mapped[datetime] = mapped_column(
#         DateTime(timezone=True),
#         nullable=False,
#         default=lambda: datetime.now(timezone.utc),
#     )

#     __table_args__ = (
#         UniqueConstraint(
#             "agent_id",
#             "version_number",
#             name="uq_agent_version",
#         ),
#     )

#     # Relationships
#     agent = relationship(
#         "Agent",
#         back_populates="versions",
#     )

#     creator = relationship(
#         "User",
#         foreign_keys=[created_by],
#     )


# # ============================================================
# # 08. TOOLS
# # ============================================================

# class Tool(Base):
#     __tablename__ = "tools"

#     id: Mapped[uuid.UUID] = mapped_column(
#         UUID(as_uuid=True),
#         primary_key=True,
#         default=uuid.uuid4,
#     )

#     name: Mapped[str] = mapped_column(
#         String(255),
#         nullable=False,
#     )

#     slug: Mapped[str] = mapped_column(
#         String(255),
#         unique=True,
#         nullable=False,
#         index=True,
#     )

#     description: Mapped[str | None] = mapped_column(
#         Text,
#         nullable=True,
#     )

#     type: Mapped[str] = mapped_column(
#         String(50),
#         nullable=False,
#     )

#     configuration_schema: Mapped[dict[str, Any] | None] = mapped_column(
#         JSONB,
#         nullable=True,
#     )

#     is_active: Mapped[bool] = mapped_column(
#         Boolean,
#         nullable=False,
#         default=True,
#     )

#     created_at: Mapped[datetime] = mapped_column(
#         DateTime(timezone=True),
#         nullable=False,
#         default=lambda: datetime.now(timezone.utc),
#     )

#     # Relationships
#     agent_tools = relationship(
#         "AgentTool",
#         back_populates="tool",
#         cascade="all, delete-orphan",
#     )

#     agents = relationship(
#         "Agent",
#         secondary="agent_tools",
#         viewonly=True,
#     )

#     tool_runs = relationship(
#         "ToolRun",
#         back_populates="tool",
#     )


# # ============================================================
# # 09. AGENT TOOLS
# # ============================================================

# class AgentTool(Base):
#     __tablename__ = "agent_tools"

#     id: Mapped[uuid.UUID] = mapped_column(
#         UUID(as_uuid=True),
#         primary_key=True,
#         default=uuid.uuid4,
#     )

#     agent_id: Mapped[uuid.UUID] = mapped_column(
#         UUID(as_uuid=True),
#         ForeignKey("agents.id", ondelete="CASCADE"),
#         nullable=False,
#         index=True,
#     )

#     tool_id: Mapped[uuid.UUID] = mapped_column(
#         UUID(as_uuid=True),
#         ForeignKey("tools.id", ondelete="CASCADE"),
#         nullable=False,
#         index=True,
#     )

#     configuration: Mapped[dict[str, Any] | None] = mapped_column(
#         JSONB,
#         nullable=True,
#     )

#     enabled: Mapped[bool] = mapped_column(
#         Boolean,
#         nullable=False,
#         default=True,
#     )

#     created_at: Mapped[datetime] = mapped_column(
#         DateTime(timezone=True),
#         nullable=False,
#         default=lambda: datetime.now(timezone.utc),
#     )

#     __table_args__ = (
#         UniqueConstraint(
#             "agent_id",
#             "tool_id",
#             name="uq_agent_tool",
#         ),
#     )

#     # Relationships
#     agent = relationship(
#         "Agent",
#         back_populates="agent_tools",
#     )

#     tool = relationship(
#         "Tool",
#         back_populates="agent_tools",
#     )


# # ============================================================
# # 10. WORKFLOWS
# # ============================================================

# class Workflow(Base):
#     __tablename__ = "workflows"

#     id: Mapped[uuid.UUID] = mapped_column(
#         UUID(as_uuid=True),
#         primary_key=True,
#         default=uuid.uuid4,
#     )

#     project_id: Mapped[uuid.UUID] = mapped_column(
#         UUID(as_uuid=True),
#         ForeignKey("projects.id", ondelete="CASCADE"),
#         nullable=False,
#         index=True,
#     )

#     name: Mapped[str] = mapped_column(
#         String(255),
#         nullable=False,
#     )

#     slug: Mapped[str] = mapped_column(
#         String(255),
#         nullable=False,
#     )

#     description: Mapped[str | None] = mapped_column(
#         Text,
#         nullable=True,
#     )

#     status: Mapped[str] = mapped_column(
#         String(50),
#         nullable=False,
#         default="draft",
#     )

#     created_by: Mapped[uuid.UUID | None] = mapped_column(
#         UUID(as_uuid=True),
#         ForeignKey("users.id", ondelete="SET NULL"),
#         nullable=True,
#         index=True,
#     )

#     created_at: Mapped[datetime] = mapped_column(
#         DateTime(timezone=True),
#         nullable=False,
#         default=lambda: datetime.now(timezone.utc),
#     )

#     updated_at: Mapped[datetime] = mapped_column(
#         DateTime(timezone=True),
#         nullable=False,
#         default=lambda: datetime.now(timezone.utc),
#         onupdate=lambda: datetime.now(timezone.utc),
#     )

#     __table_args__ = (
#         UniqueConstraint(
#             "project_id",
#             "slug",
#             name="uq_workflow_project_slug",
#         ),
#     )

#     # Relationships
#     project = relationship(
#         "Project",
#         back_populates="workflows",
#     )

#     creator = relationship(
#         "User",
#         back_populates="workflows",
#         foreign_keys=[created_by],
#     )

#     versions = relationship(
#         "WorkflowVersion",
#         back_populates="workflow",
#         cascade="all, delete-orphan",
#         order_by="WorkflowVersion.version_number",
#     )

#     variables = relationship(
#         "WorkflowVariable",
#         back_populates="workflow",
#         cascade="all, delete-orphan",
#     )

#     runs = relationship(
#         "WorkflowRun",
#         back_populates="workflow",
#         cascade="all, delete-orphan",
#     )

#     chats = relationship(
#         "Chat",
#         back_populates="workflow",
#     )

#     webhooks = relationship(
#         "Webhook",
#         back_populates="workflow",
#     )


# # ============================================================
# # 11. WORKFLOW VERSIONS
# # ============================================================

# class WorkflowVersion(Base):
#     __tablename__ = "workflow_versions"

#     id: Mapped[uuid.UUID] = mapped_column(
#         UUID(as_uuid=True),
#         primary_key=True,
#         default=uuid.uuid4,
#     )

#     workflow_id: Mapped[uuid.UUID] = mapped_column(
#         UUID(as_uuid=True),
#         ForeignKey("workflows.id", ondelete="CASCADE"),
#         nullable=False,
#         index=True,
#     )

#     version_number: Mapped[int] = mapped_column(
#         Integer,
#         nullable=False,
#     )

#     definition: Mapped[dict[str, Any]] = mapped_column(
#         JSONB,
#         nullable=False,
#         default=dict,
#     )

#     created_by: Mapped[uuid.UUID | None] = mapped_column(
#         UUID(as_uuid=True),
#         ForeignKey("users.id", ondelete="SET NULL"),
#         nullable=True,
#         index=True,
#     )

#     created_at: Mapped[datetime] = mapped_column(
#         DateTime(timezone=True),
#         nullable=False,
#         default=lambda: datetime.now(timezone.utc),
#     )

#     __table_args__ = (
#         UniqueConstraint(
#             "workflow_id",
#             "version_number",
#             name="uq_workflow_version",
#         ),
#     )

#     # Relationships
#     workflow = relationship(
#         "Workflow",
#         back_populates="versions",
#     )

#     creator = relationship(
#         "User",
#         foreign_keys=[created_by],
#     )

#     nodes = relationship(
#         "WorkflowNode",
#         back_populates="workflow_version",
#         cascade="all, delete-orphan",
#     )

#     edges = relationship(
#         "WorkflowEdge",
#         back_populates="workflow_version",
#         cascade="all, delete-orphan",
#     )

#     runs = relationship(
#         "WorkflowRun",
#         back_populates="workflow_version",
#     )


# # ============================================================
# # 12. WORKFLOW NODES
# # ============================================================

# class WorkflowNode(Base):
#     __tablename__ = "workflow_nodes"

#     id: Mapped[uuid.UUID] = mapped_column(
#         UUID(as_uuid=True),
#         primary_key=True,
#         default=uuid.uuid4,
#     )

#     workflow_version_id: Mapped[uuid.UUID] = mapped_column(
#         UUID(as_uuid=True),
#         ForeignKey("workflow_versions.id", ondelete="CASCADE"),
#         nullable=False,
#         index=True,
#     )

#     node_id: Mapped[str] = mapped_column(
#         String(255),
#         nullable=False,
#     )

#     name: Mapped[str] = mapped_column(
#         String(255),
#         nullable=False,
#     )

#     type: Mapped[str] = mapped_column(
#         String(100),
#         nullable=False,
#     )

#     position_x: Mapped[float] = mapped_column(
#         Float,
#         nullable=False,
#         default=0,
#     )

#     position_y: Mapped[float] = mapped_column(
#         Float,
#         nullable=False,
#         default=0,
#     )

#     configuration: Mapped[dict[str, Any] | None] = mapped_column(
#         JSONB,
#         nullable=True,
#     )

#     created_at: Mapped[datetime] = mapped_column(
#         DateTime(timezone=True),
#         nullable=False,
#         default=lambda: datetime.now(timezone.utc),
#     )

#     updated_at: Mapped[datetime] = mapped_column(
#         DateTime(timezone=True),
#         nullable=False,
#         default=lambda: datetime.now(timezone.utc),
#         onupdate=lambda: datetime.now(timezone.utc),
#     )

#     __table_args__ = (
#         UniqueConstraint(
#             "workflow_version_id",
#             "node_id",
#             name="uq_workflow_version_node",
#         ),
#     )

#     # Relationships
#     workflow_version = relationship(
#         "WorkflowVersion",
#         back_populates="nodes",
#     )

#     outgoing_edges = relationship(
#         "WorkflowEdge",
#         back_populates="source_node",
#         foreign_keys="WorkflowEdge.source_node_id",
#     )

#     incoming_edges = relationship(
#         "WorkflowEdge",
#         back_populates="target_node",
#         foreign_keys="WorkflowEdge.target_node_id",
#     )


# # ============================================================
# # 13. WORKFLOW EDGES
# # ============================================================

# class WorkflowEdge(Base):
#     __tablename__ = "workflow_edges"

#     id: Mapped[uuid.UUID] = mapped_column(
#         UUID(as_uuid=True),
#         primary_key=True,
#         default=uuid.uuid4,
#     )

#     workflow_version_id: Mapped[uuid.UUID] = mapped_column(
#         UUID(as_uuid=True),
#         ForeignKey("workflow_versions.id", ondelete="CASCADE"),
#         nullable=False,
#         index=True,
#     )

#     source_node_id: Mapped[uuid.UUID] = mapped_column(
#         UUID(as_uuid=True),
#         ForeignKey("workflow_nodes.id", ondelete="CASCADE"),
#         nullable=False,
#         index=True,
#     )

#     target_node_id: Mapped[uuid.UUID] = mapped_column(
#         UUID(as_uuid=True),
#         ForeignKey("workflow_nodes.id", ondelete="CASCADE"),
#         nullable=False,
#         index=True,
#     )

#     condition: Mapped[str | None] = mapped_column(
#         Text,
#         nullable=True,
#     )

#     edge_type: Mapped[str] = mapped_column(
#         String(100),
#         nullable=False,
#         default="default",
#     )

#     configuration: Mapped[dict[str, Any] | None] = mapped_column(
#         JSONB,
#         nullable=True,
#     )

#     created_at: Mapped[datetime] = mapped_column(
#         DateTime(timezone=True),
#         nullable=False,
#         default=lambda: datetime.now(timezone.utc),
#     )

#     # Relationships
#     workflow_version = relationship(
#         "WorkflowVersion",
#         back_populates="edges",
#     )

#     source_node = relationship(
#         "WorkflowNode",
#         back_populates="outgoing_edges",
#         foreign_keys=[source_node_id],
#     )

#     target_node = relationship(
#         "WorkflowNode",
#         back_populates="incoming_edges",
#         foreign_keys=[target_node_id],
#     )


# # ============================================================
# # 14. WORKFLOW VARIABLES
# # ============================================================

# class WorkflowVariable(Base):
#     __tablename__ = "workflow_variables"

#     id: Mapped[uuid.UUID] = mapped_column(
#         UUID(as_uuid=True),
#         primary_key=True,
#         default=uuid.uuid4,
#     )

#     workflow_id: Mapped[uuid.UUID] = mapped_column(
#         UUID(as_uuid=True),
#         ForeignKey("workflows.id", ondelete="CASCADE"),
#         nullable=False,
#         index=True,
#     )

#     name: Mapped[str] = mapped_column(
#         String(255),
#         nullable=False,
#     )

#     type: Mapped[str] = mapped_column(
#         String(100),
#         nullable=False,
#     )

#     default_value: Mapped[str | None] = mapped_column(
#         Text,
#         nullable=True,
#     )

#     description: Mapped[str | None] = mapped_column(
#         Text,
#         nullable=True,
#     )

#     required: Mapped[bool] = mapped_column(
#         Boolean,
#         nullable=False,
#         default=False,
#     )

#     created_at: Mapped[datetime] = mapped_column(
#         DateTime(timezone=True),
#         nullable=False,
#         default=lambda: datetime.now(timezone.utc),
#     )

#     __table_args__ = (
#         UniqueConstraint(
#             "workflow_id",
#             "name",
#             name="uq_workflow_variable_name",
#         ),
#     )

#     # Relationships
#     workflow = relationship(
#         "Workflow",
#         back_populates="variables",
#     )


# # ============================================================
# # 15. CHATS
# # ============================================================

# class Chat(Base):
#     __tablename__ = "chats"

#     id: Mapped[uuid.UUID] = mapped_column(
#         UUID(as_uuid=True),
#         primary_key=True,
#         default=uuid.uuid4,
#     )

#     workspace_id: Mapped[uuid.UUID] = mapped_column(
#         UUID(as_uuid=True),
#         ForeignKey("workspaces.id", ondelete="CASCADE"),
#         nullable=False,
#         index=True,
#     )

#     project_id: Mapped[uuid.UUID | None] = mapped_column(
#         UUID(as_uuid=True),
#         ForeignKey("projects.id", ondelete="SET NULL"),
#         nullable=True,
#         index=True,
#     )

#     user_id: Mapped[uuid.UUID] = mapped_column(
#         UUID(as_uuid=True),
#         ForeignKey("users.id", ondelete="CASCADE"),
#         nullable=False,
#         index=True,
#     )

#     agent_id: Mapped[uuid.UUID | None] = mapped_column(
#         UUID(as_uuid=True),
#         ForeignKey("agents.id", ondelete="SET NULL"),
#         nullable=True,
#         index=True,
#     )

#     workflow_id: Mapped[uuid.UUID | None] = mapped_column(
#         UUID(as_uuid=True),
#         ForeignKey("workflows.id", ondelete="SET NULL"),
#         nullable=True,
#         index=True,
#     )

#     title: Mapped[str | None] = mapped_column(
#         String(255),
#         nullable=True,
#     )

#     status: Mapped[str] = mapped_column(
#         String(50),
#         nullable=False,
#         default="active",
#     )

#     created_at: Mapped[datetime] = mapped_column(
#         DateTime(timezone=True),
#         nullable=False,
#         default=lambda: datetime.now(timezone.utc),
#     )

#     updated_at: Mapped[datetime] = mapped_column(
#         DateTime(timezone=True),
#         nullable=False,
#         default=lambda: datetime.now(timezone.utc),
#         onupdate=lambda: datetime.now(timezone.utc),
#     )

#     # Relationships
#     workspace = relationship(
#         "Workspace",
#         back_populates="chats",
#     )

#     project = relationship(
#         "Project",
#         back_populates="chats",
#     )

#     user = relationship(
#         "User",
#         back_populates="chats",
#     )

#     agent = relationship(
#         "Agent",
#         back_populates="chats",
#     )

#     workflow = relationship(
#         "Workflow",
#         back_populates="chats",
#     )

#     messages = relationship(
#         "ChatMessage",
#         back_populates="chat",
#         cascade="all, delete-orphan",
#     )


# # ============================================================
# # 16. CHAT MESSAGES
# # ============================================================

# class ChatMessage(Base):
#     __tablename__ = "chat_messages"

#     id: Mapped[uuid.UUID] = mapped_column(
#         UUID(as_uuid=True),
#         primary_key=True,
#         default=uuid.uuid4,
#     )

#     chat_id: Mapped[uuid.UUID] = mapped_column(
#         UUID(as_uuid=True),
#         ForeignKey("chats.id", ondelete="CASCADE"),
#         nullable=False,
#         index=True,
#     )

#     role: Mapped[str] = mapped_column(
#         String(50),
#         nullable=False,
#     )

#     content: Mapped[str] = mapped_column(
#         Text,
#         nullable=False,
#     )

#     model: Mapped[str | None] = mapped_column(
#         String(255),
#         nullable=True,
#     )

#     tokens_input: Mapped[int | None] = mapped_column(
#         Integer,
#         nullable=True,
#     )

#     tokens_output: Mapped[int | None] = mapped_column(
#         Integer,
#         nullable=True,
#     )

#     created_at: Mapped[datetime] = mapped_column(
#         DateTime(timezone=True),
#         nullable=False,
#         default=lambda: datetime.now(timezone.utc),
#     )

#     # Relationships
#     chat = relationship(
#         "Chat",
#         back_populates="messages",
#     )

#     attachments = relationship(
#         "MessageAttachment",
#         back_populates="message",
#         cascade="all, delete-orphan",
#     )


# # ============================================================
# # 17. MESSAGE ATTACHMENTS
# # ============================================================

# class MessageAttachment(Base):
#     __tablename__ = "message_attachments"

#     id: Mapped[uuid.UUID] = mapped_column(
#         UUID(as_uuid=True),
#         primary_key=True,
#         default=uuid.uuid4,
#     )

#     message_id: Mapped[uuid.UUID] = mapped_column(
#         UUID(as_uuid=True),
#         ForeignKey("chat_messages.id", ondelete="CASCADE"),
#         nullable=False,
#         index=True,
#     )

#     file_name: Mapped[str] = mapped_column(
#         String(255),
#         nullable=False,
#     )

#     file_url: Mapped[str] = mapped_column(
#         Text,
#         nullable=False,
#     )

#     mime_type: Mapped[str | None] = mapped_column(
#         String(255),
#         nullable=True,
#     )

#     file_size: Mapped[int | None] = mapped_column(
#         Integer,
#         nullable=True,
#     )

#     created_at: Mapped[datetime] = mapped_column(
#         DateTime(timezone=True),
#         nullable=False,
#         default=lambda: datetime.now(timezone.utc),
#     )

#     # Relationships
#     message = relationship(
#         "ChatMessage",
#         back_populates="attachments",
#     )


# # ============================================================
# # 18. AGENT RUNS
# # ============================================================

# class AgentRun(Base):
#     __tablename__ = "agent_runs"

#     id: Mapped[uuid.UUID] = mapped_column(
#         UUID(as_uuid=True),
#         primary_key=True,
#         default=uuid.uuid4,
#     )

#     agent_id: Mapped[uuid.UUID] = mapped_column(
#         UUID(as_uuid=True),
#         ForeignKey("agents.id", ondelete="CASCADE"),
#         nullable=False,
#         index=True,
#     )

#     agent_version_id: Mapped[uuid.UUID | None] = mapped_column(
#         UUID(as_uuid=True),
#         ForeignKey("agent_versions.id", ondelete="SET NULL"),
#         nullable=True,
#         index=True,
#     )

#     user_id: Mapped[uuid.UUID | None] = mapped_column(
#         UUID(as_uuid=True),
#         ForeignKey("users.id", ondelete="SET NULL"),
#         nullable=True,
#         index=True,
#     )

#     input: Mapped[dict[str, Any] | None] = mapped_column(
#         JSONB,
#         nullable=True,
#     )

#     output: Mapped[dict[str, Any] | None] = mapped_column(
#         JSONB,
#         nullable=True,
#     )

#     status: Mapped[str] = mapped_column(
#         String(50),
#         nullable=False,
#         default="pending",
#     )

#     model: Mapped[str | None] = mapped_column(
#         String(255),
#         nullable=True,
#     )

#     tokens_input: Mapped[int | None] = mapped_column(
#         Integer,
#         nullable=True,
#     )

#     tokens_output: Mapped[int | None] = mapped_column(
#         Integer,
#         nullable=True,
#     )

#     latency_ms: Mapped[int | None] = mapped_column(
#         Integer,
#         nullable=True,
#     )

#     created_at: Mapped[datetime] = mapped_column(
#         DateTime(timezone=True),
#         nullable=False,
#         default=lambda: datetime.now(timezone.utc),
#     )

#     # Relationships
#     agent = relationship(
#         "Agent",
#         back_populates="runs",
#     )

#     user = relationship(
#         "User",
#         back_populates="agent_runs",
#     )

#     agent_version = relationship(
#         "AgentVersion",
#     )

#     tool_runs = relationship(
#         "ToolRun",
#         back_populates="agent_run",
#         cascade="all, delete-orphan",
#     )


# # ============================================================
# # 19. WORKFLOW RUNS
# # ============================================================

# class WorkflowRun(Base):
#     __tablename__ = "workflow_runs"

#     id: Mapped[uuid.UUID] = mapped_column(
#         UUID(as_uuid=True),
#         primary_key=True,
#         default=uuid.uuid4,
#     )

#     workflow_id: Mapped[uuid.UUID] = mapped_column(
#         UUID(as_uuid=True),
#         ForeignKey("workflows.id", ondelete="CASCADE"),
#         nullable=False,
#         index=True,
#     )

#     workflow_version_id: Mapped[uuid.UUID | None] = mapped_column(
#         UUID(as_uuid=True),
#         ForeignKey("workflow_versions.id", ondelete="SET NULL"),
#         nullable=True,
#         index=True,
#     )

#     user_id: Mapped[uuid.UUID | None] = mapped_column(
#         UUID(as_uuid=True),
#         ForeignKey("users.id", ondelete="SET NULL"),
#         nullable=True,
#         index=True,
#     )

#     status: Mapped[str] = mapped_column(
#         String(50),
#         nullable=False,
#         default="pending",
#     )

#     input_data: Mapped[dict[str, Any] | None] = mapped_column(
#         JSONB,
#         nullable=True,
#     )

#     output_data: Mapped[dict[str, Any] | None] = mapped_column(
#         JSONB,
#         nullable=True,
#     )

#     error_message: Mapped[str | None] = mapped_column(
#         Text,
#         nullable=True,
#     )

#     started_at: Mapped[datetime | None] = mapped_column(
#         DateTime(timezone=True),
#         nullable=True,
#     )

#     completed_at: Mapped[datetime | None] = mapped_column(
#         DateTime(timezone=True),
#         nullable=True,
#     )

#     # Relationships
#     workflow = relationship(
#         "Workflow",
#         back_populates="runs",
#     )

#     workflow_version = relationship(
#         "WorkflowVersion",
#         back_populates="runs",
#     )

#     user = relationship(
#         "User",
#         back_populates="workflow_runs",
#     )

#     steps = relationship(
#         "WorkflowRunStep",
#         back_populates="workflow_run",
#         cascade="all, delete-orphan",
#     )


# # ============================================================
# # 20. WORKFLOW RUN STEPS
# # ============================================================

# class WorkflowRunStep(Base):
#     __tablename__ = "workflow_run_steps"

#     id: Mapped[uuid.UUID] = mapped_column(
#         UUID(as_uuid=True),
#         primary_key=True,
#         default=uuid.uuid4,
#     )

#     workflow_run_id: Mapped[uuid.UUID] = mapped_column(
#         UUID(as_uuid=True),
#         ForeignKey("workflow_runs.id", ondelete="CASCADE"),
#         nullable=False,
#         index=True,
#     )

#     node_id: Mapped[uuid.UUID | None] = mapped_column(
#         UUID(as_uuid=True),
#         ForeignKey("workflow_nodes.id", ondelete="SET NULL"),
#         nullable=True,
#         index=True,
#     )

#     status: Mapped[str] = mapped_column(
#         String(50),
#         nullable=False,
#         default="pending",
#     )

#     input_data: Mapped[dict[str, Any] | None] = mapped_column(
#         JSONB,
#         nullable=True,
#     )

#     output_data: Mapped[dict[str, Any] | None] = mapped_column(
#         JSONB,
#         nullable=True,
#     )

#     error_message: Mapped[str | None] = mapped_column(
#         Text,
#         nullable=True,
#     )

#     started_at: Mapped[datetime | None] = mapped_column(
#         DateTime(timezone=True),
#         nullable=True,
#     )

#     completed_at: Mapped[datetime | None] = mapped_column(
#         DateTime(timezone=True),
#         nullable=True,
#     )

#     duration_ms: Mapped[int | None] = mapped_column(
#         Integer,
#         nullable=True,
#     )

#     # Relationships
#     workflow_run = relationship(
#         "WorkflowRun",
#         back_populates="steps",
#     )

#     node = relationship(
#         "WorkflowNode",
#     )


# # ============================================================
# # 21. TOOL RUNS
# # ============================================================

# class ToolRun(Base):
#     __tablename__ = "tool_runs"

#     id: Mapped[uuid.UUID] = mapped_column(
#         UUID(as_uuid=True),
#         primary_key=True,
#         default=uuid.uuid4,
#     )

#     agent_run_id: Mapped[uuid.UUID] = mapped_column(
#         UUID(as_uuid=True),
#         ForeignKey("agent_runs.id", ondelete="CASCADE"),
#         nullable=False,
#         index=True,
#     )

#     tool_id: Mapped[uuid.UUID] = mapped_column(
#         UUID(as_uuid=True),
#         ForeignKey("tools.id", ondelete="CASCADE"),
#         nullable=False,
#         index=True,
#     )

#     input: Mapped[dict[str, Any] | None] = mapped_column(
#         JSONB,
#         nullable=True,
#     )

#     output: Mapped[dict[str, Any] | None] = mapped_column(
#         JSONB,
#         nullable=True,
#     )

#     status: Mapped[str] = mapped_column(
#         String(50),
#         nullable=False,
#         default="pending",
#     )

#     error_message: Mapped[str | None] = mapped_column(
#         Text,
#         nullable=True,
#     )

#     duration_ms: Mapped[int | None] = mapped_column(
#         Integer,
#         nullable=True,
#     )

#     created_at: Mapped[datetime] = mapped_column(
#         DateTime(timezone=True),
#         nullable=False,
#         default=lambda: datetime.now(timezone.utc),
#     )

#     # Relationships
#     agent_run = relationship(
#         "AgentRun",
#         back_populates="tool_runs",
#     )

#     tool = relationship(
#         "Tool",
#         back_populates="tool_runs",
#     )


# # ============================================================
# # 22. MODEL PROVIDERS
# # ============================================================

# class ModelProvider(Base):
#     __tablename__ = "model_providers"

#     id: Mapped[uuid.UUID] = mapped_column(
#         UUID(as_uuid=True),
#         primary_key=True,
#         default=uuid.uuid4,
#     )

#     name: Mapped[str] = mapped_column(
#         String(255),
#         nullable=False,
#     )

#     slug: Mapped[str] = mapped_column(
#         String(255),
#         unique=True,
#         nullable=False,
#         index=True,
#     )

#     base_url: Mapped[str | None] = mapped_column(
#         Text,
#         nullable=True,
#     )

#     is_active: Mapped[bool] = mapped_column(
#         Boolean,
#         nullable=False,
#         default=True,
#     )

#     created_at: Mapped[datetime] = mapped_column(
#         DateTime(timezone=True),
#         nullable=False,
#         default=lambda: datetime.now(timezone.utc),
#     )

#     # Relationships
#     models = relationship(
#         "Model",
#         back_populates="provider",
#         cascade="all, delete-orphan",
#     )


# # ============================================================
# # 23. MODELS
# # ============================================================

# class Model(Base):
#     __tablename__ = "models"

#     id: Mapped[uuid.UUID] = mapped_column(
#         UUID(as_uuid=True),
#         primary_key=True,
#         default=uuid.uuid4,
#     )

#     provider_id: Mapped[uuid.UUID] = mapped_column(
#         UUID(as_uuid=True),
#         ForeignKey("model_providers.id", ondelete="CASCADE"),
#         nullable=False,
#         index=True,
#     )

#     name: Mapped[str] = mapped_column(
#         String(255),
#         nullable=False,
#     )

#     slug: Mapped[str] = mapped_column(
#         String(255),
#         nullable=False,
#     )

#     context_window: Mapped[int | None] = mapped_column(
#         Integer,
#         nullable=True,
#     )

#     input_price: Mapped[float | None] = mapped_column(
#         Float,
#         nullable=True,
#     )

#     output_price: Mapped[float | None] = mapped_column(
#         Float,
#         nullable=True,
#     )

#     is_active: Mapped[bool] = mapped_column(
#         Boolean,
#         nullable=False,
#         default=True,
#     )

#     created_at: Mapped[datetime] = mapped_column(
#         DateTime(timezone=True),
#         nullable=False,
#         default=lambda: datetime.now(timezone.utc),
#     )

#     __table_args__ = (
#         UniqueConstraint(
#             "provider_id",
#             "slug",
#             name="uq_provider_model_slug",
#         ),
#     )

#     # Relationships
#     provider = relationship(
#         "ModelProvider",
#         back_populates="models",
#     )


# # ============================================================
# # 24. CREDENTIALS
# # ============================================================

# class Credential(Base):
#     __tablename__ = "credentials"

#     id: Mapped[uuid.UUID] = mapped_column(
#         UUID(as_uuid=True),
#         primary_key=True,
#         default=uuid.uuid4,
#     )

#     workspace_id: Mapped[uuid.UUID] = mapped_column(
#         UUID(as_uuid=True),
#         ForeignKey("workspaces.id", ondelete="CASCADE"),
#         nullable=False,
#         index=True,
#     )

#     user_id: Mapped[uuid.UUID | None] = mapped_column(
#         UUID(as_uuid=True),
#         ForeignKey("users.id", ondelete="SET NULL"),
#         nullable=True,
#         index=True,
#     )

#     name: Mapped[str] = mapped_column(
#         String(255),
#         nullable=False,
#     )

#     provider: Mapped[str] = mapped_column(
#         String(255),
#         nullable=False,
#     )

#     encrypted_data: Mapped[str] = mapped_column(
#         Text,
#         nullable=False,
#     )

#     created_at: Mapped[datetime] = mapped_column(
#         DateTime(timezone=True),
#         nullable=False,
#         default=lambda: datetime.now(timezone.utc),
#     )

#     updated_at: Mapped[datetime] = mapped_column(
#         DateTime(timezone=True),
#         nullable=False,
#         default=lambda: datetime.now(timezone.utc),
#         onupdate=lambda: datetime.now(timezone.utc),
#     )

#     # Relationships
#     workspace = relationship(
#         "Workspace",
#         back_populates="credentials",
#     )

#     user = relationship(
#         "User",
#         back_populates="credentials",
#     )


# # ============================================================
# # 25. API KEYS
# # ============================================================

# class ApiKey(Base):
#     __tablename__ = "api_keys"

#     id: Mapped[uuid.UUID] = mapped_column(
#         UUID(as_uuid=True),
#         primary_key=True,
#         default=uuid.uuid4,
#     )

#     workspace_id: Mapped[uuid.UUID] = mapped_column(
#         UUID(as_uuid=True),
#         ForeignKey("workspaces.id", ondelete="CASCADE"),
#         nullable=False,
#         index=True,
#     )

#     user_id: Mapped[uuid.UUID | None] = mapped_column(
#         UUID(as_uuid=True),
#         ForeignKey("users.id", ondelete="SET NULL"),
#         nullable=True,
#         index=True,
#     )

#     name: Mapped[str] = mapped_column(
#         String(255),
#         nullable=False,
#     )

#     key_hash: Mapped[str] = mapped_column(
#         String(255),
#         unique=True,
#         nullable=False,
#     )

#     last_used_at: Mapped[datetime | None] = mapped_column(
#         DateTime(timezone=True),
#         nullable=True,
#     )

#     expires_at: Mapped[datetime | None] = mapped_column(
#         DateTime(timezone=True),
#         nullable=True,
#     )

#     created_at: Mapped[datetime] = mapped_column(
#         DateTime(timezone=True),
#         nullable=False,
#         default=lambda: datetime.now(timezone.utc),
#     )

#     # Relationships
#     workspace = relationship(
#         "Workspace",
#         back_populates="api_keys",
#     )

#     user = relationship(
#         "User",
#         back_populates="api_keys",
#     )


# # ============================================================
# # 26. WEBHOOKS
# # ============================================================

# class Webhook(Base):
#     __tablename__ = "webhooks"

#     id: Mapped[uuid.UUID] = mapped_column(
#         UUID(as_uuid=True),
#         primary_key=True,
#         default=uuid.uuid4,
#     )

#     workspace_id: Mapped[uuid.UUID] = mapped_column(
#         UUID(as_uuid=True),
#         ForeignKey("workspaces.id", ondelete="CASCADE"),
#         nullable=False,
#         index=True,
#     )

#     workflow_id: Mapped[uuid.UUID | None] = mapped_column(
#         UUID(as_uuid=True),
#         ForeignKey("workflows.id", ondelete="SET NULL"),
#         nullable=True,
#         index=True,
#     )

#     name: Mapped[str] = mapped_column(
#         String(255),
#         nullable=False,
#     )

#     endpoint: Mapped[str] = mapped_column(
#         Text,
#         unique=True,
#         nullable=False,
#     )

#     secret_hash: Mapped[str] = mapped_column(
#         String(255),
#         nullable=False,
#     )

#     is_active: Mapped[bool] = mapped_column(
#         Boolean,
#         nullable=False,
#         default=True,
#     )

#     created_at: Mapped[datetime] = mapped_column(
#         DateTime(timezone=True),
#         nullable=False,
#         default=lambda: datetime.now(timezone.utc),
#     )

#     # Relationships
#     workspace = relationship(
#         "Workspace",
#         back_populates="webhooks",
#     )

#     workflow = relationship(
#         "Workflow",
#         back_populates="webhooks",
#     )


# # ============================================================
# # 27. ACTIVITY LOGS
# # ============================================================

# class ActivityLog(Base):
#     __tablename__ = "activity_logs"

#     id: Mapped[uuid.UUID] = mapped_column(
#         UUID(as_uuid=True),
#         primary_key=True,
#         default=uuid.uuid4,
#     )

#     workspace_id: Mapped[uuid.UUID] = mapped_column(
#         UUID(as_uuid=True),
#         ForeignKey("workspaces.id", ondelete="CASCADE"),
#         nullable=False,
#         index=True,
#     )

#     user_id: Mapped[uuid.UUID | None] = mapped_column(
#         UUID(as_uuid=True),
#         ForeignKey("users.id", ondelete="SET NULL"),
#         nullable=True,
#         index=True,
#     )

#     action: Mapped[str] = mapped_column(
#         String(255),
#         nullable=False,
#     )

#     entity_type: Mapped[str | None] = mapped_column(
#         String(100),
#         nullable=True,
#     )

#     entity_id: Mapped[uuid.UUID | None] = mapped_column(
#         UUID(as_uuid=True),
#         nullable=True,
#     )

#     metadata_: Mapped[dict[str, Any] | None] = mapped_column(
#         "metadata",
#         JSONB,
#         nullable=True,
#     )

#     created_at: Mapped[datetime] = mapped_column(
#         DateTime(timezone=True),
#         nullable=False,
#         default=lambda: datetime.now(timezone.utc),
#     )

#     # Relationships
#     workspace = relationship(
#         "Workspace",
#         back_populates="activity_logs",
#     )

#     user = relationship(
#         "User",
#         back_populates="activity_logs",
#     )


# # ============================================================
# # 28. WORKSPACE INVITATIONS
# # ============================================================

# class WorkspaceInvitation(Base):
#     __tablename__ = "workspace_invitations"

#     id: Mapped[uuid.UUID] = mapped_column(
#         UUID(as_uuid=True),
#         primary_key=True,
#         default=uuid.uuid4,
#     )

#     workspace_id: Mapped[uuid.UUID] = mapped_column(
#         UUID(as_uuid=True),
#         ForeignKey("workspaces.id", ondelete="CASCADE"),
#         nullable=False,
#         index=True,
#     )

#     email: Mapped[str] = mapped_column(
#         String(255),
#         nullable=False,
#         index=True,
#     )

#     role: Mapped[str] = mapped_column(
#         String(50),
#         nullable=False,
#         default="viewer",
#     )

#     token_hash: Mapped[str] = mapped_column(
#         String(255),
#         unique=True,
#         nullable=False,
#     )

#     invited_by: Mapped[uuid.UUID | None] = mapped_column(
#         UUID(as_uuid=True),
#         ForeignKey("users.id", ondelete="SET NULL"),
#         nullable=True,
#         index=True,
#     )

#     accepted_by: Mapped[uuid.UUID | None] = mapped_column(
#         UUID(as_uuid=True),
#         ForeignKey("users.id", ondelete="SET NULL"),
#         nullable=True,
#         index=True,
#     )

#     expires_at: Mapped[datetime] = mapped_column(
#         DateTime(timezone=True),
#         nullable=False,
#     )

#     accepted_at: Mapped[datetime | None] = mapped_column(
#         DateTime(timezone=True),
#         nullable=True,
#     )

#     created_at: Mapped[datetime] = mapped_column(
#         DateTime(timezone=True),
#         nullable=False,
#         default=lambda: datetime.now(timezone.utc),
#     )

#     # Relationships
#     workspace = relationship(
#         "Workspace",
#         back_populates="workspace_invitations",
#     )

#     inviter = relationship(
#         "User",
#         back_populates="workspace_invitations",
#         foreign_keys=[invited_by],
#     )

#     accepted_user = relationship(
#         "User",
#         foreign_keys=[accepted_by],
#     )


# # ============================================================
# # 29. KNOWLEDGE BASES
# # ============================================================

# class KnowledgeBase(Base):
#     __tablename__ = "knowledge_bases"

#     id: Mapped[uuid.UUID] = mapped_column(
#         UUID(as_uuid=True),
#         primary_key=True,
#         default=uuid.uuid4,
#     )

#     workspace_id: Mapped[uuid.UUID] = mapped_column(
#         UUID(as_uuid=True),
#         ForeignKey("workspaces.id", ondelete="CASCADE"),
#         nullable=False,
#         index=True,
#     )

#     project_id: Mapped[uuid.UUID | None] = mapped_column(
#         UUID(as_uuid=True),
#         ForeignKey("projects.id", ondelete="SET NULL"),
#         nullable=True,
#         index=True,
#     )

#     name: Mapped[str] = mapped_column(
#         String(255),
#         nullable=False,
#     )

#     description: Mapped[str | None] = mapped_column(
#         Text,
#         nullable=True,
#     )

#     embedding_model: Mapped[str | None] = mapped_column(
#         String(255),
#         nullable=True,
#         default="text-embedding-3-small",
#     )

#     created_by: Mapped[uuid.UUID | None] = mapped_column(
#         UUID(as_uuid=True),
#         ForeignKey("users.id", ondelete="SET NULL"),
#         nullable=True,
#         index=True,
#     )

#     created_at: Mapped[datetime] = mapped_column(
#         DateTime(timezone=True),
#         nullable=False,
#         default=lambda: datetime.now(timezone.utc),
#     )

#     updated_at: Mapped[datetime] = mapped_column(
#         DateTime(timezone=True),
#         nullable=False,
#         default=lambda: datetime.now(timezone.utc),
#         onupdate=lambda: datetime.now(timezone.utc),
#     )

#     # Relationships
#     workspace = relationship("Workspace", backref="knowledge_bases")
#     project = relationship("Project", backref="knowledge_bases")
#     creator = relationship("User", foreign_keys=[created_by])
#     documents = relationship("Document", back_populates="knowledge_base", cascade="all, delete-orphan")


# # ============================================================
# # 30. DOCUMENTS
# # ============================================================

# class Document(Base):
#     __tablename__ = "documents"

#     id: Mapped[uuid.UUID] = mapped_column(
#         UUID(as_uuid=True),
#         primary_key=True,
#         default=uuid.uuid4,
#     )

#     knowledge_base_id: Mapped[uuid.UUID] = mapped_column(
#         UUID(as_uuid=True),
#         ForeignKey("knowledge_bases.id", ondelete="CASCADE"),
#         nullable=False,
#         index=True,
#     )

#     file_name: Mapped[str] = mapped_column(
#         String(255),
#         nullable=False,
#     )

#     file_url: Mapped[str] = mapped_column(
#         Text,
#         nullable=False,
#     )

#     file_size: Mapped[int | None] = mapped_column(
#         Integer,
#         nullable=True,
#     )

#     mime_type: Mapped[str | None] = mapped_column(
#         String(100),
#         nullable=True,
#     )

#     status: Mapped[str] = mapped_column(
#         String(50),
#         nullable=False,
#         default="pending",
#     )

#     error_message: Mapped[str | None] = mapped_column(
#         Text,
#         nullable=True,
#     )

#     tokens_count: Mapped[int | None] = mapped_column(
#         Integer,
#         nullable=True,
#     )

#     metadata_: Mapped[dict[str, Any] | None] = mapped_column(
#         "metadata",
#         JSONB,
#         nullable=True,
#     )

#     created_at: Mapped[datetime] = mapped_column(
#         DateTime(timezone=True),
#         nullable=False,
#         default=lambda: datetime.now(timezone.utc),
#     )

#     updated_at: Mapped[datetime] = mapped_column(
#         DateTime(timezone=True),
#         nullable=False,
#         default=lambda: datetime.now(timezone.utc),
#         onupdate=lambda: datetime.now(timezone.utc),
#     )

#     # Relationships
#     knowledge_base = relationship("KnowledgeBase", back_populates="documents")

