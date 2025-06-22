import React, { useState, useEffect } from "react";
import {
  Upload,
  Link,
  FileText,
  Trash2,
  AlertCircle,
  CheckCircle,
  Clock,
  Plus,
} from "lucide-react";
import api from "../services/api";

function DocumentManager() {
  const [documents, setDocuments] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [showUploadModal, setShowUploadModal] = useState(false);
  const [uploadType, setUploadType] = useState("url");
  const [uploadData, setUploadData] = useState({
    title: "",
    url: "",
    file: null,
    text: "",
  });

  useEffect(() => {
    loadDocuments();
  }, []);

  const loadDocuments = async () => {
    try {
      const docs = await api.getDocuments();
      setDocuments(docs);
    } catch (error) {
      console.error("Error loading documents:", error);
    }
  };

  const handleUpload = async (e) => {
    e.preventDefault();
    if (!uploadData.title.trim()) {
      alert("Please enter a title");
      return;
    }

    setIsLoading(true);

    try {
      const formData = new FormData();
      formData.append("title", uploadData.title);
      formData.append("source_type", uploadType);

      if (uploadType === "url") {
        if (!uploadData.url.trim()) {
          alert("Please enter a URL");
          setIsLoading(false);
          return;
        }
        formData.append("url", uploadData.url);
      } else if (uploadType === "file") {
        if (!uploadData.file) {
          alert("Please select a file");
          setIsLoading(false);
          return;
        }
        formData.append("file", uploadData.file);
      } else if (uploadType === "text") {
        if (!uploadData.text.trim()) {
          alert("Please enter text content");
          setIsLoading(false);
          return;
        }
        formData.append("text_content", uploadData.text);
      }

      await api.uploadDocument(formData);
      setShowUploadModal(false);
      resetUploadForm();
      loadDocuments();
    } catch (error) {
      console.error("Error uploading document:", error);
      alert("Error uploading document. Please try again.");
    } finally {
      setIsLoading(false);
    }
  };

  const handleDelete = async (documentId) => {
    if (!window.confirm("Are you sure you want to delete this document?")) {
      return;
    }

    try {
      await api.deleteDocument(documentId);
      loadDocuments();
    } catch (error) {
      console.error("Error deleting document:", error);
      alert("Error deleting document. Please try again.");
    }
  };

  const resetUploadForm = () => {
    setUploadData({
      title: "",
      url: "",
      file: null,
      text: "",
    });
    setUploadType("url");
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case "completed":
        return <CheckCircle className="w-4 h-4 text-green-500" />;
      case "failed":
        return <AlertCircle className="w-4 h-4 text-red-500" />;
      case "pending":
      case "processing":
        return <Clock className="w-4 h-4 text-yellow-500" />;
      default:
        return <Clock className="w-4 h-4 text-gray-500" />;
    }
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString();
  };

  return (
    <div className="px-4 sm:px-6 lg:px-8 py-8">
      <div className="sm:flex sm:items-center mb-8">
        <div className="sm:flex-auto">
          <h1 className="text-3xl font-bold text-gray-900">Document Manager</h1>
          <p className="mt-2 text-base text-gray-700">
            Upload and manage your documentation sources for the RAG system.
          </p>
        </div>
        <div className="mt-4 sm:mt-0 sm:ml-16 sm:flex-none">
          <button
            onClick={() => setShowUploadModal(true)}
            className="inline-flex items-center justify-center rounded-md border border-transparent bg-blue-600 px-5 py-2 text-base font-semibold text-white shadow-sm hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 transition"
          >
            <Plus className="w-5 h-5 mr-2" />
            Add Document
          </button>
        </div>
      </div>

      {/* Documents Table */}
      <div className="mt-8 flow-root">
        <div className="-mx-4 -my-2 overflow-x-auto sm:-mx-6 lg:-mx-8">
          <div className="inline-block min-w-full py-2 align-middle sm:px-6 lg:px-8">
            <div className="overflow-hidden shadow ring-1 ring-black ring-opacity-5 md:rounded-lg">
              <table className="min-w-full divide-y divide-gray-300">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wide">
                      Document
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wide">
                      Type
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wide">
                      Status
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wide">
                      Chunks
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wide">
                      Date
                    </th>
                    <th className="relative px-6 py-3">
                      <span className="sr-only">Actions</span>
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {documents.length === 0 ? (
                    <tr>
                      <td
                        colSpan="6"
                        className="px-6 py-12 text-center text-lg text-gray-400"
                      >
                        <FileText className="mx-auto mb-4 w-10 h-10 text-gray-200" />
                        No documents uploaded yet.
                        <br />
                        <span className="text-sm text-gray-500">
                          Click "Add Document" to get started.
                        </span>
                      </td>
                    </tr>
                  ) : (
                    documents.map((doc) => (
                      <tr key={doc.id} className="hover:bg-blue-50 transition">
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="flex items-center">
                            <FileText className="w-5 h-5 text-gray-400 mr-3" />
                            <div>
                              <div className="text-sm font-medium text-gray-900">
                                {doc.title}
                              </div>
                              {doc.url && (
                                <div className="text-xs text-blue-600 truncate max-w-xs underline">
                                  <a
                                    href={doc.url}
                                    target="_blank"
                                    rel="noopener noreferrer"
                                  >
                                    {doc.url}
                                  </a>
                                </div>
                              )}
                              {doc.error_message && (
                                <div className="text-xs text-red-500">
                                  {doc.error_message}
                                </div>
                              )}
                            </div>
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800 capitalize">
                            {doc.source_type}
                          </span>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="flex items-center">
                            {getStatusIcon(doc.processing_status)}
                            <span className="ml-2 text-sm text-gray-900 capitalize">
                              {doc.processing_status}
                            </span>
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                          {doc.chunks_count}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {formatDate(doc.created_at)}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                          <button
                            onClick={() => handleDelete(doc.id)}
                            className="text-red-600 hover:text-red-900 focus:outline-none focus:ring-2 focus:ring-red-400 rounded"
                            title="Delete"
                          >
                            <Trash2 className="w-4 h-4" />
                          </button>
                        </td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>

      {/* Upload Modal */}
      {showUploadModal && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 flex items-center justify-center z-50">
          <div className="relative mx-auto p-6 border w-full max-w-md shadow-xl rounded-lg bg-white">
            <div className="mt-3">
              <h3 className="text-xl font-semibold text-gray-900 mb-4">
                Add New Document
              </h3>
              <form onSubmit={handleUpload}>
                <div className="mb-4">
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Document Title
                  </label>
                  <input
                    type="text"
                    value={uploadData.title}
                    onChange={(e) =>
                      setUploadData({ ...uploadData, title: e.target.value })
                    }
                    className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="Enter document title"
                    required
                    autoFocus
                  />
                </div>

                <div className="mb-4">
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Source Type
                  </label>
                  <div className="flex space-x-4">
                    <label className="flex items-center cursor-pointer">
                      <input
                        type="radio"
                        value="url"
                        checked={uploadType === "url"}
                        onChange={(e) => setUploadType(e.target.value)}
                        className="mr-2 accent-blue-600"
                      />
                      <Link className="w-4 h-4 mr-1" />
                      URL
                    </label>
                    <label className="flex items-center cursor-pointer">
                      <input
                        type="radio"
                        value="file"
                        checked={uploadType === "file"}
                        onChange={(e) => setUploadType(e.target.value)}
                        className="mr-2 accent-blue-600"
                      />
                      <Upload className="w-4 h-4 mr-1" />
                      File
                    </label>
                    <label className="flex items-center cursor-pointer">
                      <input
                        type="radio"
                        value="text"
                        checked={uploadType === "text"}
                        onChange={(e) => setUploadType(e.target.value)}
                        className="mr-2 accent-blue-600"
                      />
                      <FileText className="w-4 h-4 mr-1" />
                      Text
                    </label>
                  </div>
                </div>

                {uploadType === "url" && (
                  <div className="mb-4">
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Documentation URL
                    </label>
                    <input
                      type="url"
                      value={uploadData.url}
                      onChange={(e) =>
                        setUploadData({ ...uploadData, url: e.target.value })
                      }
                      className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                      placeholder="https://example.com/docs"
                      required
                    />
                  </div>
                )}

                {uploadType === "file" && (
                  <div className="mb-4">
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Upload File
                    </label>
                    <input
                      type="file"
                      onChange={(e) =>
                        setUploadData({
                          ...uploadData,
                          file: e.target.files[0],
                        })
                      }
                      className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                      accept=".pdf,.doc,.docx,.txt,.md,.py,.js,.html,.css,.json"
                      required
                    />
                    <p className="text-xs text-gray-500 mt-1">
                      Supported: PDF, DOC, DOCX, TXT, MD, code files
                    </p>
                  </div>
                )}

                {uploadType === "text" && (
                  <div className="mb-4">
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Text Content
                    </label>
                    <textarea
                      value={uploadData.text}
                      onChange={(e) =>
                        setUploadData({ ...uploadData, text: e.target.value })
                      }
                      className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                      rows="6"
                      placeholder="Paste your documentation text here..."
                      required
                    />
                  </div>
                )}

                <div className="flex justify-end space-x-3">
                  <button
                    type="button"
                    onClick={() => {
                      setShowUploadModal(false);
                      resetUploadForm();
                    }}
                    className="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 rounded hover:bg-gray-200 focus:outline-none focus:ring-2 focus:ring-blue-400"
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    disabled={isLoading}
                    className="px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded hover:bg-blue-700 disabled:opacity-50 focus:outline-none focus:ring-2 focus:ring-blue-400"
                  >
                    {isLoading ? "Uploading..." : "Upload"}
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
export default DocumentManager;
