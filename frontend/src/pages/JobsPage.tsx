import React, { useState, useEffect } from "react";
import { Briefcase, MapPin, DollarSign, Search, PlusCircle, X } from "lucide-react";
import { apiFetch } from "../utils/api";

interface Job {
  id: string;
  title: string;
  company: string;
  location: string | null;
  job_type: string | null;
  experience_level: string | null;
  salary_min: number | null;
  salary_max: number | null;
  currency: string;
  description: string;
  requirements: string | null;
  benefits: string | null;
  skills_required: string[] | null;
  apply_url: string | null;
}

export const JobsPage: React.FC = () => {
  const [jobs, setJobs] = useState<Job[]>([]);
  const [loading, setLoading] = useState(false);
  const [search, setSearch] = useState("");
  const [location, setLocation] = useState("");
  const [jobType, setJobType] = useState("");
  const [experienceLevel, setExperienceLevel] = useState("");

  const [selectedJob, setSelectedJob] = useState<Job | null>(null);
  const [showAddModal, setShowAddModal] = useState(false);

  // Form State for new job
  const [newJob, setNewJob] = useState({
    title: "",
    company: "",
    location: "",
    job_type: "full-time",
    experience_level: "mid",
    salary_min: "",
    salary_max: "",
    currency: "USD",
    description: "",
    requirements: "",
    benefits: "",
    skills_required: "",
    apply_url: "",
  });
  const [formError, setFormError] = useState<string | null>(null);

  const fetchJobs = async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams();
      if (search) params.append("search", search);
      if (location) params.append("location", location);
      if (jobType) params.append("job_type", jobType);
      if (experienceLevel) params.append("experience_level", experienceLevel);
      params.append("limit", "50");

      const data = await apiFetch(`/jobs?${params.toString()}`);
      setJobs(data.items || []);
    } catch (err) {
      console.error("Error fetching jobs:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchJobs();
  }, [search, location, jobType, experienceLevel]);

  const handleCreateJob = async (e: React.FormEvent) => {
    e.preventDefault();
    setFormError(null);

    try {
      const payload = {
        ...newJob,
        salary_min: newJob.salary_min ? parseFloat(newJob.salary_min) : null,
        salary_max: newJob.salary_max ? parseFloat(newJob.salary_max) : null,
        skills_required: newJob.skills_required.split(",").map((s) => s.trim()).filter(Boolean),
      };

      await apiFetch("/jobs", {
        method: "POST",
        json: payload,
      });

      setShowAddModal(false);
      // Reset form
      setNewJob({
        title: "",
        company: "",
        location: "",
        job_type: "full-time",
        experience_level: "mid",
        salary_min: "",
        salary_max: "",
        currency: "USD",
        description: "",
        requirements: "",
        benefits: "",
        skills_required: "",
        apply_url: "",
      });
      fetchJobs();
    } catch (err: any) {
      setFormError(err.message || "Failed to create job listings.");
    }
  };

  return (
    <div className="animate-fade-in" style={styles.container}>
      {/* Header */}
      <div style={styles.header}>
        <div>
          <h1 style={styles.title}>Browse Positions</h1>
          <p style={styles.subtitle}>Filter, search, or publish database listings.</p>
        </div>
        <button onClick={() => setShowAddModal(true)} className="btn btn-primary">
          <PlusCircle size={18} />
          <span>Post a Job</span>
        </button>
      </div>

      {/* Search Filter Box */}
      <div className="card" style={styles.filterCard}>
        <div style={styles.filterRow}>
          <div style={styles.searchWrap}>
            <Search size={18} color="#6b7280" style={styles.searchIcon} />
            <input
              type="text"
              className="form-input"
              placeholder="Search title, company, skills..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              style={styles.searchInput}
            />
          </div>

          <div style={styles.selectWrap}>
            <MapPin size={16} color="#6b7280" style={styles.selectIcon} />
            <input
              type="text"
              className="form-input"
              placeholder="City, State, Remote..."
              value={location}
              onChange={(e) => setLocation(e.target.value)}
              style={styles.selectInput}
            />
          </div>

          <select
            className="form-input"
            value={jobType}
            onChange={(e) => setJobType(e.target.value)}
            style={styles.selectOption}
          >
            <option value="">All Job Types</option>
            <option value="full-time">Full Time</option>
            <option value="part-time">Part Time</option>
            <option value="remote">Remote</option>
            <option value="contract">Contract</option>
          </select>

          <select
            className="form-input"
            value={experienceLevel}
            onChange={(e) => setExperienceLevel(e.target.value)}
            style={styles.selectOption}
          >
            <option value="">All Levels</option>
            <option value="junior">Junior</option>
            <option value="mid">Mid-level</option>
            <option value="senior">Senior</option>
          </select>
        </div>
      </div>

      {/* Main Panel Content */}
      <div style={styles.contentLayout}>
        {/* Jobs List */}
        <div style={styles.listSection}>
          {loading ? (
            <div style={styles.statusBox}>Loading job openings...</div>
          ) : jobs.length === 0 ? (
            <div style={styles.statusBox}>No jobs matching your filters were found. Try modifying searches.</div>
          ) : (
            <div style={styles.listGrid}>
              {jobs.map((job) => (
                <div
                  key={job.id}
                  onClick={() => setSelectedJob(job)}
                  className="card"
                  style={{
                    ...styles.jobCard,
                    borderColor: selectedJob?.id === job.id ? "#6366f1" : "#374151",
                  }}
                >
                  <div style={styles.jobCardHeader}>
                    <h3 style={styles.jobTitle}>{job.title}</h3>
                    <span style={styles.companyTag}>{job.company}</span>
                  </div>

                  <div style={styles.metaRow}>
                    <div style={styles.metaItem}>
                      <MapPin size={14} />
                      <span>{job.location || "Remote"}</span>
                    </div>
                    <div style={styles.metaItem}>
                      <Briefcase size={14} />
                      <span style={{ textTransform: "capitalize" }}>{job.job_type || "N/A"}</span>
                    </div>
                    {(job.salary_min || job.salary_max) && (
                      <div style={styles.metaItem}>
                        <DollarSign size={14} />
                        <span>
                          {job.salary_min ? `${job.salary_min.toLocaleString()}` : "0"} -{" "}
                          {job.salary_max ? `${job.salary_max.toLocaleString()}` : "Max"}{" "}
                          {job.currency}
                        </span>
                      </div>
                    )}
                  </div>

                  {job.skills_required && job.skills_required.length > 0 && (
                    <div style={styles.skillRow}>
                      {job.skills_required.slice(0, 4).map((skill) => (
                        <span key={skill} className="badge badge-info">
                          {skill}
                        </span>
                      ))}
                      {job.skills_required.length > 4 && (
                        <span style={styles.moreSkills}>+{job.skills_required.length - 4} more</span>
                      )}
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Selected Job Detail Panel */}
        <div style={styles.detailSection}>
          {selectedJob ? (
            <div className="card card-glass" style={styles.detailCard}>
              <h2 style={styles.detailTitle}>{selectedJob.title}</h2>
              <h3 style={styles.detailCompany}>{selectedJob.company}</h3>

              <div style={styles.detailMetaGrid}>
                <div style={styles.detailMetaLabel}>Location:</div>
                <div style={styles.detailMetaVal}>{selectedJob.location || "Remote"}</div>

                <div style={styles.detailMetaLabel}>Type:</div>
                <div style={{ ...styles.detailMetaVal, textTransform: "capitalize" }}>
                  {selectedJob.job_type || "Full Time"}
                </div>

                <div style={styles.detailMetaLabel}>Experience:</div>
                <div style={{ ...styles.detailMetaVal, textTransform: "capitalize" }}>
                  {selectedJob.experience_level || "Mid Level"}
                </div>

                {selectedJob.salary_min && (
                  <>
                    <div style={styles.detailMetaLabel}>Compensation:</div>
                    <div style={styles.detailMetaVal}>
                      {selectedJob.salary_min.toLocaleString()} - {selectedJob.salary_max?.toLocaleString()}{" "}
                      {selectedJob.currency}
                    </div>
                  </>
                )}
              </div>

              {/* Required skills */}
              {selectedJob.skills_required && selectedJob.skills_required.length > 0 && (
                <div style={{ marginBottom: "1.5rem" }}>
                  <h4 style={styles.sectionHeader}>Required Skills</h4>
                  <div style={styles.detailSkillsGrid}>
                    {selectedJob.skills_required.map((skill) => (
                      <span key={skill} className="badge badge-info" style={{ fontSize: "0.8rem" }}>
                        {skill}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {/* Description */}
              <div style={{ marginBottom: "1.5rem" }}>
                <h4 style={styles.sectionHeader}>Job Description</h4>
                <p style={styles.detailParagraph}>{selectedJob.description}</p>
              </div>

              {/* Requirements */}
              {selectedJob.requirements && (
                <div style={{ marginBottom: "1.5rem" }}>
                  <h4 style={styles.sectionHeader}>Job Requirements</h4>
                  <p style={styles.detailParagraph}>{selectedJob.requirements}</p>
                </div>
              )}

              {/* Apply Button */}
              {selectedJob.apply_url && (
                <a
                  href={selectedJob.apply_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="btn btn-primary"
                  style={{ width: "100%", textDecoration: "none" }}
                >
                  Apply Directly
                </a>
              )}
            </div>
          ) : (
            <div style={styles.noDetailBox}>
              <Briefcase size={40} color="#374151" />
              <p>Select a job listing to view complete descriptions and requirements.</p>
            </div>
          )}
        </div>
      </div>

      {/* Post a Job Modal Overlay */}
      {showAddModal && (
        <div style={styles.modalOverlay}>
          <div className="card animate-fade-in" style={styles.modalCard}>
            <div style={styles.modalHeader}>
              <h2 style={{ fontSize: "1.5rem", fontWeight: 700 }}>Post a New Job</h2>
              <button onClick={() => setShowAddModal(false)} style={styles.closeBtn}>
                <X size={20} />
              </button>
            </div>

            {formError && (
              <div style={styles.formErrorBox}>
                <span>{formError}</span>
              </div>
            )}

            <form onSubmit={handleCreateJob} style={styles.formScroll}>
              <div style={styles.formRow}>
                <div className="form-group" style={{ flex: 1 }}>
                  <label className="form-label">Job Title *</label>
                  <input
                    type="text"
                    required
                    className="form-input"
                    placeholder="e.g. Software Engineer"
                    value={newJob.title}
                    onChange={(e) => setNewJob({ ...newJob, title: e.target.value })}
                  />
                </div>
                <div className="form-group" style={{ flex: 1 }}>
                  <label className="form-label">Company Name *</label>
                  <input
                    type="text"
                    required
                    className="form-input"
                    placeholder="e.g. Tech Solutions"
                    value={newJob.company}
                    onChange={(e) => setNewJob({ ...newJob, company: e.target.value })}
                  />
                </div>
              </div>

              <div style={styles.formRow}>
                <div className="form-group" style={{ flex: 1 }}>
                  <label className="form-label">Location (City, Remote)</label>
                  <input
                    type="text"
                    className="form-input"
                    placeholder="e.g. San Francisco, CA or Remote"
                    value={newJob.location}
                    onChange={(e) => setNewJob({ ...newJob, location: e.target.value })}
                  />
                </div>
                <div className="form-group" style={{ flex: 0.5 }}>
                  <label className="form-label">Job Type</label>
                  <select
                    className="form-input"
                    value={newJob.job_type}
                    onChange={(e) => setNewJob({ ...newJob, job_type: e.target.value })}
                  >
                    <option value="full-time">Full Time</option>
                    <option value="part-time">Part Time</option>
                    <option value="remote">Remote</option>
                    <option value="contract">Contract</option>
                  </select>
                </div>
                <div className="form-group" style={{ flex: 0.5 }}>
                  <label className="form-label">Experience Level</label>
                  <select
                    className="form-input"
                    value={newJob.experience_level}
                    onChange={(e) => setNewJob({ ...newJob, experience_level: e.target.value })}
                  >
                    <option value="junior">Junior</option>
                    <option value="mid">Mid Level</option>
                    <option value="senior">Senior</option>
                  </select>
                </div>
              </div>

              <div style={styles.formRow}>
                <div className="form-group" style={{ flex: 1 }}>
                  <label className="form-label">Min Salary</label>
                  <input
                    type="number"
                    className="form-input"
                    placeholder="80000"
                    value={newJob.salary_min}
                    onChange={(e) => setNewJob({ ...newJob, salary_min: e.target.value })}
                  />
                </div>
                <div className="form-group" style={{ flex: 1 }}>
                  <label className="form-label">Max Salary</label>
                  <input
                    type="number"
                    className="form-input"
                    placeholder="120000"
                    value={newJob.salary_max}
                    onChange={(e) => setNewJob({ ...newJob, salary_max: e.target.value })}
                  />
                </div>
                <div className="form-group" style={{ flex: 0.5 }}>
                  <label className="form-label">Currency</label>
                  <input
                    type="text"
                    className="form-input"
                    placeholder="USD"
                    value={newJob.currency}
                    onChange={(e) => setNewJob({ ...newJob, currency: e.target.value })}
                  />
                </div>
              </div>

              <div className="form-group">
                <label className="form-label">Skills Required (Comma separated)</label>
                <input
                  type="text"
                  className="form-input"
                  placeholder="Python, React, Docker, Git"
                  value={newJob.skills_required}
                  onChange={(e) => setNewJob({ ...newJob, skills_required: e.target.value })}
                />
              </div>

              <div className="form-group">
                <label className="form-label">Apply URL</label>
                <input
                  type="url"
                  className="form-input"
                  placeholder="https://company.com/apply"
                  value={newJob.apply_url}
                  onChange={(e) => setNewJob({ ...newJob, apply_url: e.target.value })}
                />
              </div>

              <div className="form-group">
                <label className="form-label">Job Description * (Min 10 chars)</label>
                <textarea
                  required
                  className="form-input"
                  placeholder="Describe the job duties, role functions, and tech stack details..."
                  rows={4}
                  value={newJob.description}
                  onChange={(e) => setNewJob({ ...newJob, description: e.target.value })}
                  style={{ resize: "vertical" }}
                />
              </div>

              <div className="form-group">
                <label className="form-label">Job Requirements</label>
                <textarea
                  className="form-input"
                  placeholder="Candidate requirements, degree, years of experience..."
                  rows={3}
                  value={newJob.requirements}
                  onChange={(e) => setNewJob({ ...newJob, requirements: e.target.value })}
                  style={{ resize: "vertical" }}
                />
              </div>

              <div style={{ marginTop: "2rem", display: "flex", justifyContent: "flex-end", gap: "1rem" }}>
                <button
                  type="button"
                  onClick={() => setShowAddModal(false)}
                  className="btn btn-secondary"
                >
                  Cancel
                </button>
                <button type="submit" className="btn btn-primary">
                  Publish Job
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

const styles = {
  container: {
    maxWidth: "1200px",
    margin: "0 auto",
  },
  header: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    borderBottom: "1px solid #1f2937",
    paddingBottom: "1.5rem",
    marginBottom: "1.5rem",
  },
  title: {
    fontSize: "2.25rem",
    fontWeight: 800,
    color: "#fff",
  },
  subtitle: {
    fontSize: "1rem",
    color: "#9ca3af",
    marginTop: "0.25rem",
  },
  filterCard: {
    padding: "1.25rem",
    marginBottom: "1.5rem",
    backgroundColor: "#111827",
  },
  filterRow: {
    display: "flex",
    gap: "1rem",
    flexWrap: "wrap" as const,
  },
  searchWrap: {
    flex: 1.5,
    position: "relative" as const,
    display: "flex",
    alignItems: "center",
    minWidth: "220px",
  },
  searchIcon: {
    position: "absolute" as const,
    left: "12px",
  },
  searchInput: {
    paddingLeft: "2.5rem",
  },
  selectWrap: {
    flex: 1,
    position: "relative" as const,
    display: "flex",
    alignItems: "center",
    minWidth: "160px",
  },
  selectIcon: {
    position: "absolute" as const,
    left: "12px",
  },
  selectInput: {
    paddingLeft: "2.5rem",
  },
  selectOption: {
    flex: 0.8,
    minWidth: "140px",
    cursor: "pointer",
  },
  contentLayout: {
    display: "flex",
    gap: "2rem",
    alignItems: "flex-start",
  },
  listSection: {
    flex: 1.2,
    minWidth: "360px",
  },
  listGrid: {
    display: "flex",
    flexDirection: "column" as const,
    gap: "1rem",
  },
  jobCard: {
    cursor: "pointer",
    padding: "1.25rem 1.5rem",
    borderWidth: "1px",
    borderStyle: "solid",
    borderRadius: "10px",
    backgroundColor: "#111827",
  },
  jobCardHeader: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "flex-start",
    marginBottom: "0.5rem",
    gap: "1rem",
  },
  jobTitle: {
    fontSize: "1.1rem",
    fontWeight: 700,
    color: "#fff",
  },
  companyTag: {
    fontSize: "0.75rem",
    fontWeight: 600,
    color: "#6366f1",
    padding: "0.25rem 0.5rem",
    backgroundColor: "rgba(99, 102, 241, 0.1)",
    borderRadius: "6px",
    whiteSpace: "nowrap" as const,
  },
  metaRow: {
    display: "flex",
    gap: "1rem",
    fontSize: "0.8rem",
    color: "#9ca3af",
    marginBottom: "1rem",
    flexWrap: "wrap" as const,
  },
  metaItem: {
    display: "flex",
    alignItems: "center",
    gap: "0.4rem",
  },
  skillRow: {
    display: "flex",
    flexWrap: "wrap" as const,
    gap: "0.4rem",
    alignItems: "center",
  },
  moreSkills: {
    fontSize: "0.75rem",
    color: "#6b7280",
    fontWeight: 500,
    marginLeft: "0.25rem",
  },
  statusBox: {
    textAlign: "center" as const,
    padding: "3rem",
    color: "#9ca3af",
    backgroundColor: "#111827",
    border: "1px dashed #374151",
    borderRadius: "12px",
    fontSize: "0.95rem",
  },
  detailSection: {
    flex: 0.8,
    position: "sticky" as const,
    top: "2.5rem",
    minWidth: "300px",
  },
  detailCard: {
    padding: "2rem",
    backgroundColor: "#111827",
  },
  detailTitle: {
    fontSize: "1.5rem",
    fontWeight: 800,
    color: "#fff",
    marginBottom: "0.25rem",
  },
  detailCompany: {
    fontSize: "1rem",
    fontWeight: 600,
    color: "#6366f1",
    marginBottom: "1.5rem",
  },
  detailMetaGrid: {
    display: "grid",
    gridTemplateColumns: "100px 1fr",
    gap: "0.75rem",
    fontSize: "0.85rem",
    color: "#9ca3af",
    borderBottom: "1px solid #374151",
    paddingBottom: "1.5rem",
    marginBottom: "1.5rem",
  },
  detailMetaLabel: {
    fontWeight: 600,
  },
  detailMetaVal: {
    color: "#fff",
  },
  sectionHeader: {
    fontSize: "0.95rem",
    fontWeight: 700,
    color: "#fff",
    textTransform: "uppercase" as const,
    letterSpacing: "0.05em",
    marginBottom: "0.75rem",
  },
  detailSkillsGrid: {
    display: "flex",
    flexWrap: "wrap" as const,
    gap: "0.5rem",
  },
  detailParagraph: {
    fontSize: "0.9rem",
    color: "#cbd5e1",
    lineHeight: "1.6",
    whiteSpace: "pre-line" as const,
  },
  noDetailBox: {
    display: "flex",
    flexDirection: "column" as const,
    alignItems: "center",
    justifyContent: "center",
    textAlign: "center" as const,
    padding: "5rem 2rem",
    backgroundColor: "#11182750",
    border: "1px dashed #374151",
    borderRadius: "12px",
    color: "#9ca3af",
    gap: "1rem",
    fontSize: "0.875rem",
  },
  modalOverlay: {
    position: "fixed" as const,
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    backgroundColor: "rgba(0, 0, 0, 0.75)",
    backdropFilter: "blur(4px)",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    zIndex: 1000,
    padding: "2rem",
  },
  modalCard: {
    width: "100%",
    maxWidth: "720px",
    maxHeight: "90vh",
    display: "flex",
    flexDirection: "column" as const,
    backgroundColor: "#111827",
    padding: "2rem",
  },
  modalHeader: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    borderBottom: "1px solid #374151",
    paddingBottom: "1rem",
    marginBottom: "1.5rem",
  },
  closeBtn: {
    backgroundColor: "transparent",
    border: "none",
    color: "#9ca3af",
    cursor: "pointer",
  },
  formScroll: {
    overflowY: "auto" as const,
    flex: 1,
    paddingRight: "0.5rem",
  },
  formRow: {
    display: "flex",
    gap: "1.5rem",
    marginBottom: "0.5rem",
  },
  formErrorBox: {
    padding: "0.75rem",
    backgroundColor: "rgba(239, 68, 68, 0.1)",
    border: "1px solid rgba(239, 68, 68, 0.2)",
    borderRadius: "8px",
    color: "#fca5a5",
    fontSize: "0.85rem",
    marginBottom: "1rem",
  },
};
export default JobsPage;
