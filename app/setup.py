from abstracts.models import Work, Version

w1 = Work(work_id = 1)
w2 = Work(work_id = 2)

v1 = Version(work_id = w1,
            title = 'foo',
            type = 'submitted',
            year = 2015,
            state = 'new',
             full_text= 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Pellentesque mauris est, dapibus vitae tempor quis, iaculis ac neque. Nulla accumsan eget justo eu posuere. Morbi hendrerit porta felis. Proin condimentum eros id mi finibus, sit amet porttitor mauris dictum. Fusce ac mi eros. Quisque a felis pellentesque, suscipit diam dignissim, dapibus nisi. Nunc consectetur congue purus at venenatis. Pellentesque tincidunt ante sodales maximus dictum.')

v2 = Version(work_id=w1,
             title='Foo',
             type='submitted',
             year=2015,
             state='new',
             full_text='Lorem ipsum dolor sit amet, consectetur adipiscing elit. Pellentesque mauris est, dapibus vitae tempor quis, iaculis ac neque. Nulla accumsan eget justo eu posuere. Morbi hendrerit porta felis. Proin condimentum eros id mi finibus, sit amet porttitor mauris dictum. Fusce ac mi eros. Quisque a felis pellentesque, suscipit diam dignissim, dapibus nisi. Nunc consectetur congue purus at venenatis. Pellentesque tincidunt ante sodales maximus dictum. Curabitur ut commodo odio.             Mauris at leo iaculis, tristique justo a, fringilla urna. Vestibulum ante ipsum primis in faucibus orci luctus et ultrices posuere cubilia Cu')

v3 = Version(work_id=w2,
             title='bar',
             type='submitted',
             year=2014,
             state='new',
             full_text='Lorem ipsum dolor sit amet, consectetur adipiscing elit. Pellentesque mauris est, dapibus vitae tempor quis, iaculis ac neque. Nulla accumsan eget justo eu posuere. Morbi hendrerit porta felis. Proin condimentum eros id mi finibus, sit amet porttitor mauris dictum. Fusce ac mi eros. Quisque a felis pellentesque, suscipit diam dignissim, dapibus nisi. Nunc consectetur congue purus at venenatis. Pellentesque tincidunt ante sodales maximus dictum. Curabitur ut commodo odio.             Mauris at leo ia')

w1.save()
w2.save()
v1.save()
v2.save()
v3.save()

