import requests
import sys
import io


class AIStudyNotesAPITester:
    def __init__(self, base_url="https://notes-mapper-1.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0
        self.uploaded_files = []
        self.created_notes = []
        self.created_mindmaps = []

    def run_test(self, name, method, endpoint, expected_status, data=None, files=None):
        """Run a single API test"""
        url = f"{self.api_url}/{endpoint}"
        headers = {}

        if files is None:
            headers["Content-Type"] = "application/json"

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")

        try:
            if method == "GET":
                response = requests.get(url, headers=headers)

            elif method == "POST":
                if files:
                    response = requests.post(url, files=files)
                else:
                    response = requests.post(url, json=data, headers=headers)

            elif method == "DELETE":
                response = requests.delete(url, headers=headers)

            else:
                print(f"❌ Unsupported method: {method}")
                return False, {}

            success = response.status_code == expected_status

            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")

                try:
                    response_data = response.json()
                    if isinstance(response_data, dict) and "id" in response_data:
                        print(f"   Response ID: {response_data['id']}")
                    return True, response_data
                except Exception:
                    return True, {}

            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                try:
                    print(f"   Error: {response.json()}")
                except Exception:
                    print(f"   Error: {response.text}")
                return False, {}

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def test_root_endpoint(self):
        return self.run_test("Root API Endpoint", "GET", "", 200)[0]

    def test_file_upload(self):
        """Test file upload functionality"""
        test_content = (
            "This is a test study note about machine learning.\n"
            "It covers basic concepts and algorithms."
        )

        test_file = io.BytesIO(test_content.encode("utf-8"))

        files = {
            "file": ("test_notes.txt", test_file, "text/plain")
        }

        success, response = self.run_test(
            "File Upload (TXT)",
            "POST",
            "upload",
            200,
            files=files
        )

        if success and "id" in response:
            self.uploaded_files.append(response)
            print(f"   Uploaded file ID: {response['id']}")
            print(f"   Extracted text length: {len(response.get('extracted_text', ''))}")

        return success

    def test_get_files(self):
        success, response = self.run_test("Get All Files", "GET", "files", 200)

        if success and isinstance(response, list):
            print(f"   Found {len(response)} files")
            self.uploaded_files.extend(
                [file for file in response if file not in self.uploaded_files]
            )

        return success

    def test_process_notes(self):
        if not self.uploaded_files:
            print("❌ No files available for processing notes")
            return False

        file_ids = [self.uploaded_files[0]["id"]]

        success, response = self.run_test(
            "Process Combined Notes",
            "POST",
            "process-notes",
            200,
            data={
                "file_ids": file_ids,
                "title": "Test Combined Notes"
            }
        )

        if success and "id" in response:
            self.created_notes.append(response)
            print(f"   Created note ID: {response['id']}")
            print(f"   Content length: {len(response.get('content', ''))}")

        return success

    def test_get_combined_notes(self):
        success, response = self.run_test(
            "Get Combined Notes",
            "GET",
            "combined-notes",
            200
        )

        if success and isinstance(response, list):
            print(f"   Found {len(response)} combined notes")
            self.created_notes.extend(
                [note for note in response if note not in self.created_notes]
            )

        return success

    def test_generate_mindmap(self):
        if not self.uploaded_files:
            print("❌ No files available for generating mind map")
            return False

        file_ids = [self.uploaded_files[0]["id"]]

        success, response = self.run_test(
            "Generate Mind Map",
            "POST",
            "generate-mindmap",
            200,
            data={
                "file_ids": file_ids,
                "title": "Test Mind Map"
            }
        )

        if success and "id" in response:
            self.created_mindmaps.append(response)
            print(f"   Created mindmap ID: {response['id']}")
            print(f"   Nodes count: {len(response.get('nodes', []))}")
            print(f"   Edges count: {len(response.get('edges', []))}")

        return success

    def test_get_mindmaps(self):
        success, response = self.run_test("Get Mind Maps", "GET", "mindmaps", 200)

        if success and isinstance(response, list):
            print(f"   Found {len(response)} mind maps")
            self.created_mindmaps.extend(
                [m for m in response if m not in self.created_mindmaps]
            )

        return success

    def test_delete_file(self):
        if not self.uploaded_files:
            print("❌ No files available for deletion")
            return False

        file_to_delete = self.uploaded_files[0]

        success, _ = self.run_test(
            "Delete File",
            "DELETE",
            f"files/{file_to_delete['id']}",
            200
        )

        if success:
            self.uploaded_files.remove(file_to_delete)
            print(f"   Deleted file: {file_to_delete.get('filename', 'unknown')}")

        return success

    def test_delete_note(self):
        if not self.created_notes:
            print("❌ No notes available for deletion")
            return False

        note_to_delete = self.created_notes[0]

        success, _ = self.run_test(
            "Delete Combined Note",
            "DELETE",
            f"combined-notes/{note_to_delete['id']}",
            200
        )

        if success:
            self.created_notes.remove(note_to_delete)
            print(f"   Deleted note: {note_to_delete.get('title', 'unknown')}")

        return success

    def test_delete_mindmap(self):
        if not self.created_mindmaps:
            print("❌ No mind maps available for deletion")
            return False

        mindmap_to_delete = self.created_mindmaps[0]

        success, _ = self.run_test(
            "Delete Mind Map",
            "DELETE",
            f"mindmaps/{mindmap_to_delete['id']}",
            200
        )

        if success:
            self.created_mindmaps.remove(mindmap_to_delete)
            print(f"   Deleted mindmap: {mindmap_to_delete.get('title', 'unknown')}")

        return success


def main():
    print("🚀 Starting AI Study Notes API Testing...")
    print("=" * 60)

    tester = AIStudyNotesAPITester()

    tests = [
        ("Root Endpoint", tester.test_root_endpoint),
        ("File Upload", tester.test_file_upload),
        ("Get Files", tester.test_get_files),
        ("Process Notes", tester.test_process_notes),
        ("Get Combined Notes", tester.test_get_combined_notes),
        ("Generate Mind Map", tester.test_generate_mindmap),
        ("Get Mind Maps", tester.test_get_mindmaps),
        ("Delete File", tester.test_delete_file),
        ("Delete Note", tester.test_delete_note),
        ("Delete Mind Map", tester.test_delete_mindmap),
    ]

    failed_tests = []

    for test_name, test_func in tests:
        try:
            if not test_func():
                failed_tests.append(test_name)
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {str(e)}")
            failed_tests.append(test_name)

    print("\n" + "=" * 60)
    print("📊 TEST RESULTS")
    print("=" * 60)
    print(f"Tests passed: {tester.tests_passed}/{tester.tests_run}")

    if tester.tests_run > 0:
        print(f"Success rate: {(tester.tests_passed / tester.tests_run) * 100:.1f}%")

    if failed_tests:
        print(f"\n❌ Failed tests: {', '.join(failed_tests)}")
        return 1
    else:
        print("\n✅ All tests passed!")
        return 0


if __name__ == "__main__":
    sys.exit(main())